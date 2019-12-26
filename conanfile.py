from conans import ConanFile, tools, MSBuild
import os
import shutil

class AceConan(ConanFile):
    name = "ACE"
    version = "6.5.6"
    license = "<Put the package license here>"
    author = "patrik.fiedler@gmx.de"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Ace here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def source(self):
        tools.get("http://github.com/DOCGroup/ACE_TAO/releases/download/ACE%2BTAO-6_5_6/ACE-6.5.6.tar.gz")

    def build(self):
        if tools.os_info.is_windows and self.settings.compiler == "Visual Studio":
            f = open("ACE_wrappers/ace/config.h", "a")
            f.write("""#include "ace/config-win32.h"
""")
            f.close()
            if self.settings.compiler.version == 14:
                vsString = "14"
            if self.settings.compiler.version == 15:
                vsString = "2017"
            if self.settings.compiler.version == 16:
                vsString = "2019"
            sln_file = "ACE_wrappers/ACE_wrappers_vs%s.sln" % vsString
            msbuild = MSBuild(self)
            winsdk_version = self._find_windows_10_sdk()
            if not winsdk_version:
                raise Exception("Windows 10 SDK wasn't found")
            self.output.info("set windows 10 sdk to %s" % winsdk_version)
            msbuild.build(sln_file, targets=["ACE"], arch=self.settings.arch, build_type=self.settings.build_type, winsdk_version=winsdk_version )
        if tools.os_info.is_linux:
            f = open("ACE_wrappers/ace/config.h", "a")
            f.write("""#include "ace/config-linux.h"
""")
            f.close()
            shutil.copyfile("ACE_wrappers/ace/config-linux.h", "ACE_wrappers/ace/config.h") 
            os.environ["ACE_ROOT"] = os.getcwd() + "/ACE_wrappers"
            shutil.copyfile( os.getcwd() + "/ACE_wrappers/include/makeinclude/platform_linux.GNU",  os.getcwd() + "/ACE_wrappers/include/makeinclude/platform_macros.GNU") 
            n_cores = tools.cpu_count()
            self.run("cd ACE_wrappers && make -j%s" % n_cores )
    def package(self):
        self.copy("*", dst="include/ace", src="ACE_wrappers/ace")
        self.copy("*", dst="lib", src="ACE_wrappers/lib")

    def package_info(self):
        if tools.os_info.is_windows and self.settings.compiler == "Visual Studio" and self.settings.build_type == "Debug":
            self.cpp_info.libs = ["ACEd"]
        else:
            self.cpp_info.libs = ["ACE"]

    # copied from conan, need to make expose it
    def _system_registry_key(self, key, subkey, query):
        from six.moves import winreg  # @UnresolvedImport
        try:
            hkey = winreg.OpenKey(key, subkey)
        except (OSError, WindowsError):  # Raised by OpenKey/Ex if the function fails (py3, py2)
            return None
        else:
            try:
                value, _ = winreg.QueryValueEx(hkey, query)
                return value
            except EnvironmentError:
                return None
            finally:
                winreg.CloseKey(hkey)

    def _find_windows_10_sdk(self):
        """finds valid Windows 10 SDK version which can be passed to vcvarsall.bat (vcvars_command)"""
        # uses the same method as VCVarsQueryRegistry.bat
        from six.moves import winreg  # @UnresolvedImport
        hives = [
            (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Wow6432Node'),
            (winreg.HKEY_CURRENT_USER, r'SOFTWARE\Wow6432Node'),
            (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE'),
            (winreg.HKEY_CURRENT_USER, r'SOFTWARE')
        ]
        for key, subkey in hives:
            subkey = r'%s\Microsoft\Microsoft SDKs\Windows\v10.0' % subkey
            installation_folder = self._system_registry_key(key, subkey, 'InstallationFolder')
            if installation_folder:
                if os.path.isdir(installation_folder):
                    include_dir = os.path.join(installation_folder, 'include')
                    for sdk_version in os.listdir(include_dir):
                        if (os.path.isdir(os.path.join(include_dir, sdk_version))
                                and sdk_version.startswith('10.')):
                            windows_h = os.path.join(include_dir, sdk_version, 'um', 'Windows.h')
                            if os.path.isfile(windows_h):
                                return sdk_version
        return None
