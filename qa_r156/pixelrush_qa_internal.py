"""PIXEL RUSH R156 QA: instrumentacao interna exclusiva do APK de diagnostico.

Nao altera estado de jogo, RNG, SDL ou renderizacao. Nunca publica em producao.
"""
from __future__ import annotations
import atexit
from collections import deque
import functools
import json
import os
from pathlib import Path
import threading
import time

QA_VERSION = "R156_v3.279.08_QA"
MAX_LABELS = 80
MAX_SAMPLES = 1024
LOG_EVERY_NS = 10_000_000_000
CPROFILE_DELAY_FRAMES = 45
CPROFILE_WINDOW_NS = 10_000_000_000
_lock = threading.Lock()
_stats = {}
_last_frame = 0
_frames = 0
_started = time.perf_counter_ns()
_next_log = _started + LOG_EVERY_NS
_prof = None
_prof_begin = 0
_prof_done = False
_output_error = False

def _storage_dir():
    base = os.environ.get("ANDROID_PRIVATE") or os.environ.get("PIXELRUSH_QA_DIR") or os.getcwd()
    return Path(base) / "pixelrush_qa_internal"

def _emit(record):
    global _output_error
    try:
        directory = _storage_dir()
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / "r156_metrics.jsonl").open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(record, ensure_ascii=True, separators=(",", ":")) + "\n")
    except Exception:
        _output_error = True
        try:
            print("PIXELRUSH_R156_QA " + json.dumps(record, separators=(",", ":")), flush=True)
        except Exception:
            pass

def _record(label, elapsed_ns, cpu_ns=None):
    try:
        if elapsed_ns < 0:
            return
        with _lock:
            d = _stats.get(label)
            if d is None:
                if len(_stats) >= MAX_LABELS:
                    return
                d = _stats[label] = {"total_ns": 0, "cpu_ns": 0, "count": 0, "max_ns": 0,
                                     "samples_ns": deque(maxlen=MAX_SAMPLES)}
            d["count"] += 1
            d["total_ns"] += elapsed_ns
            d["max_ns"] = max(d["max_ns"], elapsed_ns)
            if cpu_ns is not None and cpu_ns >= 0:
                d["cpu_ns"] += cpu_ns
            d["samples_ns"].append(elapsed_ns)
    except Exception:
        pass

def measure(label):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter_ns()
            c0 = time.thread_time_ns() if hasattr(time, "thread_time_ns") else 0
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = time.perf_counter_ns() - start
                c1 = time.thread_time_ns() if c0 else 0
                _record(label, elapsed, c1 - c0 if c0 else None)
        return wrapper
    return deco

def _percentile(values, p):
    if not values:
        return None
    seq = sorted(values)
    return round(seq[min(len(seq) - 1, max(0, int((len(seq) - 1) * p + .5)))] / 1e6, 3)

def _snapshot(now):
    global _next_log
    with _lock:
        out = {}
        for name, d in _stats.items():
            n = d["count"]
            vals = tuple(d["samples_ns"])
            out[name] = {"calls": n, "mean_ms": round(d["total_ns"] / max(n, 1) / 1e6, 3),
                         "total_ms": round(d["total_ns"] / 1e6, 3),
                         "cpu_total_ms": round(d["cpu_ns"] / 1e6, 3),
                         "p95_ms_recent": _percentile(vals, .95),
                         "p99_ms_recent": _percentile(vals, .99),
                         "worst_ms": round(d["max_ns"] / 1e6, 3),
                         "recent_samples": len(vals)}
    _emit({"type": "snapshot", "qa_version": QA_VERSION, "monotonic_ns": now,
           "wallclock_unix_ns": time.time_ns(), "elapsed_s": round((now - _started) / 1e9, 3),
           "frames_seen": _frames, "stats": out,
           "cprofile_running": bool(_prof), "storage_fallback": _output_error})
    _next_log = now + LOG_EVERY_NS

def _profile_transition(now):
    global _prof, _prof_begin, _prof_done
    if _prof_done:
        return
    if _prof is None:
        if _frames < CPROFILE_DELAY_FRAMES:
            return
        try:
            import cProfile
            profile = cProfile.Profile()
            profile.enable()
            _prof = profile
            _prof_begin = now
            _emit({"type": "cprofile_start", "monotonic_ns": now, "qa_version": QA_VERSION,
                   "warning": "cProfile acrescenta sobrecarga; nao usar para medir FPS de producao"})
        except Exception as error:
            _prof_done = True
            _emit({"type": "cprofile_unavailable", "error": type(error).__name__})
    elif now - _prof_begin >= CPROFILE_WINDOW_NS:
        profile = _prof
        _prof = None
        _prof_done = True
        try:
            profile.disable()
            path = _storage_dir() / "r156_python_calls.prof"
            path.parent.mkdir(parents=True, exist_ok=True)
            t0 = time.perf_counter_ns()
            profile.dump_stats(str(path))
            _emit({"type": "cprofile_saved", "path": str(path),
                   "duration_s": round((now - _prof_begin) / 1e9, 3),
                   "flush_ms": round((time.perf_counter_ns() - t0) / 1e6, 3)})
        except Exception as error:
            _emit({"type": "cprofile_save_error", "error": type(error).__name__})

def frame_tick():
    global _frames, _last_frame
    try:
        now = time.perf_counter_ns()
        if _last_frame:
            _record("FRAME_PRESENT_INTERVAL", now - _last_frame)
        _frames += 1
        _last_frame = now
        if now >= _next_log:
            _snapshot(now)
        _profile_transition(now)
    except Exception:
        pass

def _finish():
    try:
        if _prof is not None:
            _prof.disable()
        _snapshot(time.perf_counter_ns())
    except Exception:
        pass

atexit.register(_finish)
