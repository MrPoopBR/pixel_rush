"""Receita EXPERIMENTAL para pygame-ce 2.5.8 em Android ARM64/SDL2.

Nao homologada: exige compilacao real e auditoria ELF/16 KiB.
Baseada nas receitas p4a pygame e nas propostas abertas #2971/#2838.
"""
from os.path import join
from pathlib import Path

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
            # O template Android 2.5.8 nao lista system; os saves Android usam
            # pygame.system.get_pref_path() e requerem a extensao nativa.
            if not any(line.startswith("system ") for line in setup.splitlines()):
                setup += "\nsystem src_c/system.c $(SDL) $(DEBUG)\n"
            if not any(line.startswith("system ") for line in setup.splitlines()):
                raise RuntimeError("pygame.system ausente do Setup Android")
            Path("Setup").write_text(setup)


recipe = PixelRushPygameCeRecipe()
