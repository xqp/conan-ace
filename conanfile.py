from conans import ConanFile, tools, MSBuild

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
            sln_file = "ACE_wrappers/ACE_vs%s.sln" % vsString
            msbuild = MSBuild(self)
            msbuild.build(sln_file, targets=["ACE"])


    def package(self):
        self.copy("*", dst="include/ace", src="ACE_wrappers/ace")
        self.copy("*", dst="lib", src="ACE_wrappers/lib")

    def package_info(self):
        self.cpp_info.libs = ["ACE"]
