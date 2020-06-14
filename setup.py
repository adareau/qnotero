#!/usr/bin/env python3

#  This file is part of Qnotero.
#
#      Qnotero is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      Qnotero is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with Qnotero.  If not, see <https://www.gnu.org/licenses/>.
#      Copyright (c) 2019 E. Albiter


from libqnotero.qnotero import Qnotero
import sys
# Use cx_Freeze to make the windows installer and MacOS bundle
if sys.platform == 'linux':
    import glob
    from distutils.core import setup
else:
    from cx_Freeze import setup, Executable

base = None
packages = []
package_data = {}
scripts = []
data_files = []
options = {}
executables = []
if sys.platform == 'win32':
    base = 'Win32GUI'
    # Setup options for windows
    options = {
        'build_exe': {
            'optimize': '2',
            'silent': '0',
            'includes': [
                'sip'
            ],
            'packages': [
                "libqnotero",
                "libzotero",
                "libqnotero._themes",
                "libzotero._noteProvider",
            ],
            'include_files': [
                'resources',
                'data\qnotero.ico',
            ],
        },
    }
    executables = [
        Executable(
            'qnotero',
            base=base,
            icon='data\qnotero.ico',
        )
    ]
    setup(name="qnotero",
          version=Qnotero.version,
          description="Standalone sidekick to the Zotero reference manager",
          author="E. Albiter",
          author_email="ealbitere@ipn.mx",
          url="https://github.com/ealbiter/qnotero",
          scripts=scripts,
          packages=packages,
          package_data=package_data,
          data_files=data_files,
          options=options,
          executables=executables
          )
elif sys.platform == 'darwin':
    # Setup options for MacOs
    options = {
        'build_exe': {
            'optimize': '2',
            'silent': '0',
            'includes': [
                # 'sip'
            ],
            'packages': [
                "libqnotero",
                "libzotero",
                "libqnotero._themes",
                "libzotero._noteProvider",
            ],
            'include_files': [
                ('resources/dark', 'themes/dark'),
                ('resources/light', 'themes/light')
            ],
        },
        'bdist_mac': {
            'iconfile': 'resources/qnotero.icns',
            'bundle_name': 'Qnotero',
            'custom_info_plist': 'resources/info.plist'
        }
    }
    executables = [
        Executable(
            'qnotero',
            base=base,
            icon='resources/qnotero.icns',
        )
    ]
    setup(name="qnotero",
          version=Qnotero.version,
          description="Standalone sidekick to the Zotero reference manager",
          author="E. Albiter",
          author_email="ealbitere@ipn.mx",
          url="https://github.com/ealbiter/qnotero",
          scripts=scripts,
          packages=packages,
          package_data=package_data,
          data_files=data_files,
          options=options,
          executables=executables
          )
else:  # Setup options for Linux

    packages = [
        "libqnotero",
        "libzotero",
        "libqnotero._themes",
        "libzotero._noteProvider",
        "libqnotero.qt"
    ]
    package_data = {
        "libqnotero": ["ui/*.ui"],
    }
    scripts = ["qnotero"]
    data_files = [
        ("/usr/share/qnotero", ["COPYING"]),
        ("/usr/share/applications", ["data/qnotero.desktop"]),
        ("/usr/share/qnotero/resources", glob.glob("resources/*.svg")),
        ("/usr/share/qnotero/resources/light",
         glob.glob("resources/light/*")),
        ("/usr/share/qnotero/resources/dark",
         glob.glob("resources/dark/*")),
    ]
    setup(name="qnotero",
          version=Qnotero.version,
          description="Standalone sidekick to the Zotero reference manager",
          author="E. Albiter",
          author_email="ealbitere@ipn.mx",
          url="https://github.com/ealbiter/qnotero",
          scripts=scripts,
          packages=packages,
          package_data=package_data,
          data_files=data_files,
          options=options
          )
