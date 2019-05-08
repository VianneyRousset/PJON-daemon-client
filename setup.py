#!/usr/bin/env python

'''
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, version 3.

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

from sys import version_info
from distutils.core import setup
import re
import os.path

if version_info < (3, 5):
    raise RuntimeError("PJON-daemon-client requires at least Python 3.5")

HERE = os.path.dirname(__file__)
SOURCE_FILE = os.path.join(HERE, 'src', 'service', '__init__.py')

def get_version(fpath):
    with open(fpath, encoding='utf8') as f:
        for line in f:
            m = re.match(r"""__version__\s*=\s*['"](.*)['"]""", line)
            if m:
                return m.groups()[0]
        raise RuntimeError("Failed to get version")


setup(name='PJON-daemon-client',
      version=get_version('PJON_daemon_client/__init__.py'),
      description='Connect to a PJON-daemon, listen and send messages',
      author='Vianney Rousset',
      maintainer='Vianney Rousset',
      url='https://github.com/VianneyRousset/PJON-daemon-client',
      license="GPL3",
      packages=['PJON_daemon_client'],
      keywords='PJON daemon client connection'.split(),
      classifiers=[
          # Reference: http://pypi.python.org/pypi?%3Aaction=list_classifiers
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Operating System :: POSIX",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      )


