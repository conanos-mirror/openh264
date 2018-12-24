from conans import ConanFile, tools, AutoToolsBuildEnvironment, Meson
from conanos.build import config_scheme
import os


class OpenH264Conan(ConanFile):
    name = "openh264"
    version = "1.8.0"
    description = "Open Source H.264 Codec"
    url = "https://github.com/conanos/openh264"
    homepage = 'http://www.openh264.org/'
    license = "BSD"
    patch = 'win-module-def.patch'
    exports = ["LICENSE", patch]
    generators = "visual_studio", "gcc"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = { 'shared': True, 'fPIC': True }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def source(self):
        #url_="https://github.com/cisco/openh264/archive/v{version}.tar.gz"
        url_="http://172.16.64.65:8081/artifactory/gstreamer/openh264-{version}.tar.gz"
        tools.get(url_.format(version=self.version))
        if self.settings.os == 'Windows':
            tools.patch(patch_file=self.patch)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        prefix = os.path.join(self.build_folder, self._build_subfolder, "install")
        defs = {'prefix' : prefix}
        if self.settings.os == "Linux":
            defs.update({'libdir':'lib'})
        meson = Meson(self)
        meson.configure(defs=defs,source_dir=self._source_subfolder, build_dir=self._build_subfolder)
        meson.build()
        self.run('ninja -C {0} install'.format(meson.build_dir))

    #    if self.settings.compiler == 'Visual Studio':
    #        msys_bin = self.deps_env_info['msys2_installer'].MSYS_BIN
    #        with tools.environment_append({'PATH': [msys_bin],
    #                                       'CONAN_BASH_PATH': os.path.join(msys_bin, 'bash.exe')}):
    #            with tools.vcvars(self.settings, filter_known_paths=False, force=True):
    #                self.build_configure()
    #    else:
    #        self.build_configure()

    #def build_configure(self):
    #    with tools.chdir(self.source_subfolder):
    #        prefix = os.path.abspath(self.package_folder)
    #        if self.settings.compiler == 'Visual Studio':
    #            prefix = tools.unix_path(prefix, tools.MSYS2)
    #        tools.replace_in_file('Makefile', 'PREFIX=/usr/local', 'PREFIX=%s' % prefix)
    #        if self.settings.arch == 'x86':
    #            arch = 'i386'
    #        elif self.settings.arch == 'x86_64':
    #            arch = 'x86_64'
    #        args = ['ARCH=%s' % arch]

    #        env_build = AutoToolsBuildEnvironment(self)
    #        if self.settings.compiler == 'Visual Studio':
    #            tools.replace_in_file(os.path.join('build', 'platform-msvc.mk'),
    #                                  'CFLAGS_OPT += -MT',
    #                                  'CFLAGS_OPT += -%s' % str(self.settings.compiler.runtime))
    #            tools.replace_in_file(os.path.join('build', 'platform-msvc.mk'),
    #                                  'CFLAGS_DEBUG += -MTd -Gm',
    #                                  'CFLAGS_DEBUG += -%s -Gm' % str(self.settings.compiler.runtime))
    #            args.append('OS=msvc')
    #            env_build.flags.append('-FS')
    #        elif self.settings.compiler == 'clang' and self.settings.compiler.libcxx == 'libc++':
    #            tools.replace_in_file('Makefile', 'STATIC_LDFLAGS=-lstdc++', 'STATIC_LDFLAGS=-lc++\nLDFLAGS+=-lc++')
    #        env_build.make(args=args)
    #        args.append('install')
    #        env_build.make(args=args)

    def package(self):
        self.copy("*", dst=self.package_folder, src=os.path.join(self.build_folder,self._build_subfolder, "install"))
        #self.copy(pattern="LICENSE", dst="licenses", src=self.source_subfolder)
        #if self.options.shared:
        #    exts = ['*.a']
        #else:
        #    exts = ['*.dll', '*.so*', '*.dylib*']
        #for root, _, filenames in os.walk(self.package_folder):
        #    for ext in exts:
        #        for filename in fnmatch.filter(filenames, ext):
        #            os.unlink(os.path.join(root, filename))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        #if self.settings.compiler == 'Visual Studio' and self.options.shared:
        #    self.cpp_info.libs = ['openh264_dll']
        #else:
        #    self.cpp_info.libs = ['openh264']
        #if self.settings.os == "Linux":
        #    self.cpp_info.libs.append('pthread')
