#!/usr/bin/env python
import os

from distutils.core import setup
from distutils.command.build_py import build_py as _build_py
from distutils.command.install_data import install_data as _install_data

packages= [ 'maxwidgets'
          , 'maxwidgets.extra_guiqwt'
          , 'maxwidgets.extra_guiqwt.ui'
          , 'maxwidgets.input'
          , 'maxwidgets.display'
          , 'maxwidgets.panel'
          ]

env_script = 'maxwidgets.sh'
env_script_src = """
EXTRA_TAURUS_PATHS="{0}"

for path in $EXTRA_TAURUS_PATHS; do
    if ! echo $TAURUSQTDESIGNERPATH | grep -q $path; then
        TAURUSQTDESIGNERPATH=$path:$TAURUSQTDESIGNERPATH
    fi
done

export TAURUSQTDESIGNERPATH
"""

def ui_to_py(arg, dirname, names):
    cwd = os.getcwd()
    os.chdir(dirname)
    for name in names:
        if not name.endswith('.ui'):
            continue

        pyname = 'ui_' + name.replace('.ui', '.py')

        cmd = 'taurusuic4 -o %s %s' % (pyname, name)
        ok = not(os.system(cmd))

        src = os.path.join(dirname, name)
        dst = os.path.join(dirname, pyname)
        print ok and "[OK]" or "[FAIL]", src, '->', dst

    os.chdir(cwd)


class build_py(_build_py):

    def _build_ui_modules(self):
        os.path.walk('src', ui_to_py, None)

    def run(self):
        self._build_ui_modules()
        _build_py.run(self)


class install_data(_install_data):

    def _create_env_script(self):
        install_cmd = self.get_finalized_command('install')
        root   = getattr(install_cmd, 'root')
        libdir = getattr(install_cmd, 'install_lib')

        if root is not None:
            libdir = os.sep + os.path.relpath(libdir,root)
        extra_taurus_paths = set()

        for package in packages:
            try:
                pkg, subdir = package.split('.')[:2]
            except:
                continue
            extra_taurus_paths.add(os.path.join(libdir, pkg, subdir))

        extra_taurus_paths = ' '.join(extra_taurus_paths)

        with open(env_script, 'w') as ofile:
            text = env_script_src.format(extra_taurus_paths)
            ofile.write(text)

    def run(self):
        self._create_env_script()
        _install_data.run(self)

setup(name = 'python-maxwidgets',
      version = '0.9.5',
      description = 'A collection of reusable Taurus widgets',
      packages = packages,
      package_dir = {'maxwidgets' : 'src'},
      data_files = [('/etc/profile.d', [env_script])],
      cmdclass = {#'build_py' : build_py,
                  'install_data' : install_data},
     )
