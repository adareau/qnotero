#!/usr/bin/env python3

"""
This file is part of qnotero.

qnotero is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

qnotero is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with qnotero.  If not, see <http://www.gnu.org/licenses/>.
"""

import glob
from libqnotero.qnotero import Qnotero
from distutils.core import setup

setup(name="qnotero",
      version=Qnotero.version,
      description="Standalone sidekick to the Zotero reference manager",
      author="E. Albiter",
      author_email="ealbitere@ipn.mx",
      url="",
      scripts=["qnotero"],
      packages=[
          "libqnotero",
          "libzotero",
          "libqnotero._themes",
          "libzotero._noteProvider",
          "libqnotero.qt"
      ],
      package_data={
          "libqnotero": ["ui/*.ui"],
      },
      data_files=[
          ("/usr/share/qnotero", ["COPYING"]),
          ("/usr/share/applications", ["data/qnotero.desktop"]),
          ("/usr/share/qnotero/resources", glob.glob("resources/*.svg")),
          ("/usr/share/qnotero/resources/light",
           glob.glob("resources/light/*")),
          ("/usr/share/qnotero/resources/dark",
           glob.glob("resources/dark/*")),
      ]
      )
