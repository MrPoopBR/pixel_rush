"""Receita EXPERIMENTAL para pygame-ce 2.5.8 em Android ARM64/SDL2.

Nao homologada: exige compilacao real e auditoria ELF/16 KiB.
Baseada nas receitas p4a pygame e nas propostas abertas #2971/#2838.
"""
from os.path import join
from pathlib import Path

import sh
from pythonforandroid.logger import info, shprint
from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.toolchain import current_directory


class PixelRushPygameCeRecipe(CompiledComponentsPythonRecipe):
    name = "pygame-ce"
    version = "2.5.8"
    url = "https://github.com/pygame-community/pygame-ce/archive/refs/tags/{version}.tar.gz"
    site_packages_name = "pygame"
    depends = ["sdl2", "sdl2_image", "sdl2_mixer", "sdl2_ttf",
               "setuptools", "jpeg", "png"]
    min_ndk_api_support = 24
    call_hostpython_via_targetpython = False
    install_in_hostpython = False

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        env["USE_SDL2"] = "1"
        env["PYGAME_CROSS_COMPILE"] = "TRUE"
        env["PYGAME_ANDROID"] = "TRUE"
        env["ANDROID_ROOT"] = join(self.ctx.ndk.sysroot, "usr")
        env["LDFLAGS"] = (
            env.get("LDFLAGS", "") + " -Wl,-z,max-page-size=16384"
        ).strip()
        env["CFLAGS"] = (env.get("CFLAGS", "") + " -fPIC").strip()
        return env

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            template = Path("buildconfig/Setup.Android.SDL2.in").read_text()
            png = self.get_recipe("png", self.ctx)
            jpeg = self.get_recipe("jpeg", self.ctx)
            image = self.get_recipe("sdl2_image", self.ctx)
            mixer = self.get_recipe("sdl2_mixer", self.ctx)
            lib_dirs = (
                " -L" + join(self.ctx.bootstrap.build_dir, "libs", arch.arch)
                + " -L" + join(png.get_build_dir(arch.arch), ".libs")
                + " -L" + jpeg.get_build_dir(arch.arch)
                + " -L" + arch.ndk_lib_dir_versioned
            )
            setup = template.format(
                sdl_includes=(
                    " -I" + join(self.ctx.bootstrap.build_dir, "jni", "SDL", "include")
                    + lib_dirs
                ),
                sdl_ttf_includes=(
                    " -I" + join(self.ctx.bootstrap.build_dir, "jni", "SDL2_ttf")
                    + " -I" + join(self.ctx.bootstrap.build_dir, "jni", "SDL2_ttf", "include")
                ),
                sdl_image_includes=" ".join(
                    "-I" + str(x) for x in image.get_include_dirs(arch)
                ),
                sdl_mixer_includes=" ".join(
                    "-I" + str(x) for x in mixer.get_include_dirs(arch)
                ),
                jpeg_includes="-I" + jpeg.get_build_dir(arch.arch),
                png_includes="-I" + png.get_build_dir(arch.arch),
                freetype_includes="",
            )
            if not any(line.startswith("system ") for line in setup.splitlines()):
                setup += "\nsystem src_c/system.c $(SDL) $(DEBUG)\n"
            if not any(line.startswith("system ") for line in setup.splitlines()):
                raise RuntimeError("pygame.system ausente do Setup Android")
            Path("Setup").write_text(setup)

    def install_python_package(self, arch, name=None, env=None, is_dir=True):
        """Instala extensoes ja compiladas via setuptools, sem novo build PEP 517/Meson.

        Na execucao 41212545595, a implementacao p4a usa 'pip install .' e
        aciona Meson sem cross-file: ele tenta rodar um binario ARM64 em Linux.
        O build_ext da receita ja foi concluido; usamos o legado setup.py install
        para reutilizar esse build sem executar um sanity check do Meson.
        """
        if env is None:
            env = self.get_recipe_env(arch)
        source = self.get_build_dir(arch.arch)
        target = self.ctx.get_python_install_dir(arch.arch)
        record = join(source, "pygame-ce-android-install-record.txt")
        info("Installing pygame-ce via setuptools legacy setup.py (no PEP 517/Meson)")
        with current_directory(source):
            shprint(
                sh.Command(self.hostpython_location), "setup.py", "install",
                "--single-version-externally-managed", "--record", record,
                "--install-lib", target, _env=env,
            )
        package = Path(target) / "pygame"
        if not (package / "__init__.py").is_file():
            raise RuntimeError("pygame-ce: pacote pygame nao foi instalado")
        for module in ("base", "system"):
            if not tuple(package.glob(module + "*.so")):
                raise RuntimeError("pygame-ce: modulo nativo ausente: " + module)


recipe = PixelRushPygameCeRecipe()
