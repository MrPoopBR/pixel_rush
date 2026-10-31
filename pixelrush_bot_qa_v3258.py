"""Ponte HTTP local para bot QA — v3.258.0. Não inicia no jogo normal.

HTTP sem TLS, por isso somente loopback por padrão. O servidor NÃO toca
Pygame: cada chamada vira comando numa fila consumida na thread do jogo.
"""
from __future__ import annotations
from collections import deque
from hmac import compare_digest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import ipaddress
import json
from threading import Lock, Thread

ACTIONS = frozenset(('jump','duck_down','duck_up','pause','start','noop'))
MAX_BODY = 1024


class EstadoBot:
    def __init__(self, token, *, capacity=32):
        if not isinstance(token,str) or len(token)<16 or len(token)>256:
            raise ValueError('Token de QA deve ter entre 16 e 256 caracteres')
        self._token=token
        self._queue=deque()
        self._lock=Lock()
        self._capacity=capacity
        self._frame=0
        self._player=None
        self._running=False
        self._connected=0

    def autorizado(self, header):
        return isinstance(header,str) and compare_digest(header, 'Bearer '+self._token)

    def enfileirar(self,action):
        if action not in ACTIONS: raise ValueError('Ação não permitida')
        with self._lock:
            if len(self._queue)>=self._capacity: return False
            self._queue.append(action)
            return True

    def drenar(self):
        with self._lock:
            actions=list(self._queue)
            self._queue.clear()
        return actions

    def quadro(self, frame, player=None):
        with self._lock:
            self._frame=int(frame)
            self._player=player
            self._running=True

    def estado(self):
        with self._lock:
            return {'schema':'pixelrush.bot_qa.v1','versao':'v3.258.0',
                    'frame':self._frame,'jogo_executando':self._running,
                    'jogador':self._player,'fila_pendente':len(self._queue)}


def iniciar_servidor(estado,host='127.0.0.1',port=8765,*,allow_lan=False,observador=None):
    try:
        endereco=ipaddress.ip_address(host)
    except ValueError as exc:
        raise ValueError('Use somente um IP literal para bind') from exc
    if not endereco.is_loopback and not allow_lan:
        raise ValueError('Host externo exige --allow-lan explícito')
    if not 0 <= port <= 65535:
        raise ValueError('Porta inválida')

    class API(BaseHTTPRequestHandler):
        def log_message(self,fmt,*args):
            # Não registrar tokens nem dados de usuários.
            pass
        def _answer(self,status,data):
            raw=json.dumps(data,ensure_ascii=False,separators=(',',':')).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Cache-Control','no-store')
            self.send_header('Content-Length',str(len(raw)))
            self.end_headers();self.wfile.write(raw)
        def _authorized(self):
            if not estado.autorizado(self.headers.get('Authorization')):
                self._answer(401,{'erro':'não autorizado'})
                return False
            return True
        def do_GET(self):
            if not self._authorized():return
            if self.path=='/v1/observation':
                if observador is None:
                    return self._answer(404,{'erro':'observação desativada neste backend'})
                try:
                    return self._answer(200,observador())
                except BlockingIOError:
                    return self._answer(429,{'erro':'aguarde para solicitar outra captura'})
                except (OSError,ValueError,RuntimeError) as ex:
                    return self._answer(503,{'erro':'captura indisponível','tipo':type(ex).__name__})
            if self.path=='/v1/state': self._answer(200,estado.estado())
            elif self.path=='/v1/health': self._answer(200,{'ok':True,'schema':'pixelrush.bot_qa.v1'})
            else: self._answer(404,{'erro':'rota desconhecida'})
        def do_POST(self):
            if not self._authorized():return
            if self.path!='/v1/action':
                return self._answer(404,{'erro':'rota desconhecida'})
            try:
                n=int(self.headers.get('Content-Length','-1'))
                if n<0 or n>MAX_BODY:raise ValueError('corpo inválido')
                value=json.loads(self.rfile.read(n))
                if not isinstance(value,dict) or set(value)!={'action'} or not isinstance(value['action'],str):
                    raise ValueError('JSON: apenas action como string')
                if value['action'] not in ACTIONS:raise ValueError('ação desconhecida')
            except (ValueError,UnicodeDecodeError,json.JSONDecodeError):
                return self._answer(400,{'erro':'comando inválido'})
            if not estado.enfileirar(value['action']):
                return self._answer(429,{'erro':'fila cheia'})
            self._answer(202,{'aceito':True})
    server=ThreadingHTTPServer((host,port),API)
    server.daemon_threads=True
    thread=Thread(target=server.serve_forever,daemon=True,name='PixelRushBotQA')
    thread.start()
    return server,thread


class AdaptadorPygame:
    """Traduz comandos autorizados em eventos Pygame na thread principal.

    Só use no lançador externo de QA. Não intercepta saves, spawn nem física.
    """
    def __init__(self,estado,pygame):
        self.estado=estado
        self.pg=pygame
        self.held=set()
        self.eventos_orig=pygame.event.get
        self.teclas_orig=pygame.key.get_pressed

    def eventos(self,*args,**kwargs):
        pg=self.pg
        eventos=list(self.eventos_orig(*args,**kwargs))
        for acao in self.estado.drenar():
            if acao=='jump':
                eventos.extend([pg.event.Event(pg.KEYDOWN,key=pg.K_SPACE),
                                pg.event.Event(pg.KEYUP,key=pg.K_SPACE)])
            elif acao=='duck_down':
                self.held.add(pg.K_DOWN)
                eventos.append(pg.event.Event(pg.KEYDOWN,key=pg.K_DOWN))
            elif acao=='duck_up':
                self.held.discard(pg.K_DOWN)
                eventos.append(pg.event.Event(pg.KEYUP,key=pg.K_DOWN))
            elif acao=='pause':
                eventos.append(pg.event.Event(pg.KEYDOWN,key=pg.K_p))
            elif acao=='start':
                for t in (pg.MOUSEBUTTONDOWN,pg.MOUSEBUTTONUP):
                    eventos.append(pg.event.Event(t,pos=(225,374),button=1))
        return eventos

    def teclas(self):
        base=self.teclas_orig()
        held=self.held.copy()
        class Teclas:
            def __getitem__(self,k):return bool(base[k] or k in held)
        return Teclas()

    def instalar(self):
        self.pg.event.get=self.eventos
        self.pg.key.get_pressed=self.teclas

    def remover(self):
        self.pg.event.get=self.eventos_orig
        self.pg.key.get_pressed=self.teclas_orig
