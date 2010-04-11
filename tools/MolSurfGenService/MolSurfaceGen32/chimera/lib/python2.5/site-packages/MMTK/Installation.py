# Some utility functions for compilation and installation of
# MMTK add-on packages.
#
# Written by Konrad Hinsen
# last revision: 1999-9-2
#

_undocumented = 1

import os, string, sys

# Package path
mmtk_package_path = os.path.split(__file__)[0]

# Include path
include_path = os.path.join(mmtk_package_path, "Include")

# Shared library path
shared_library_path = os.path.join(mmtk_package_path, sys.platform)

# Make sure that everything is recompiled if the last compile was for a
# different OS or a different Python version.
def checkVersion():
    if os.path.exists('version_info'):
        info = open('version_info').readlines()
        platform = string.strip(info[0])
        version = string.strip(info[1])
        if sys.platform != platform or sys.version != version:
            os.system('make distclean')
            for file in ['Makefile.pre.in', 'Makefile.pre', 'Makefile',
                         'Setup']:
                if os.path.exists(file):
                    os.unlink(file)
    open('version_info', 'w').write(sys.platform+'\n' + sys.version+'\n')

# Get a copy of Makefile.pre.in from the Python installation.
def copyMakefile():
    if not os.path.exists('Makefile.pre.in'):
        lib = os.path.join(os.path.join(sys.exec_prefix, 'lib'),
                           'python'+sys.version[:3])
        source = os.path.join(os.path.join(lib, 'config'), 'Makefile.pre.in')
        if os.path.exists(source):
            os.system('cp ' + source + ' .')
        else:
            raise IOError, \
                  "Makefile.pre.in not found; check the Python installation"

# Make the Setup file from a template inserting the MMTK include directory.
def makeSetup():
    if not os.path.exists('Setup'):
        import Scientific.Installation
        os.system("cat Setup.template | sed -e s+@MMTK@+" + include_path +
                  "+g | sed -e s+@SCIENTIFIC@+" +
                  Scientific.Installation.include_path + "+g > Setup")

# Create the Makefile.
def makeMakefile():
    if not os.path.exists('Makefile'):
        os.system("make -f Makefile.pre.in boot")

# Compile the modules.
def makeModules():
    os.system("make")

# Execute all compilation steps.
def compileModules():
    checkVersion()
    copyMakefile()
    makeSetup()
    makeMakefile()
    makeModules()

# Copy the shared modules to their destination directory.
def installSharedModules(module_names = None):
    lib = os.path.join(os.path.join(sys.exec_prefix, 'lib'),
                       'python'+sys.version[:3])
    makefile = os.path.join(os.path.join(lib, 'config'), 'Makefile')
    os.system("grep '^SO' " + makefile + " > temp")
    line = open("temp").readlines()[0]
    os.unlink("temp")
    extension = string.strip(line[string.find(line, '=')+1:])
    if module_names is None:
        os.system("cp *" + extension + " " + shared_library_path)
    else:
        for module in module_names:
            module = module + extension
            os.system("cp " + module + " " + shared_library_path)

# Copy the Python modules to their destination directory
def installPythonModules(path=None):
    import os, compileall
    if path is None:
        path = os.getcwd()
    compileall.compile_dir(path)
    os.chdir(path)
    os.system("cp -r * " + mmtk_package_path)
