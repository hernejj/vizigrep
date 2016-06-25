#!/usr/bin/python

import os
from setuptools import setup, Command

# Customize 'setup.py clean' to remove unwanted build artifacts
class CleanCommand(Command):
    user_options = [
        ('all', None, '(--all, required by deb build process)')
    ]

    def initialize_options(self):
        self.all = False

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -rf ./build ./dist ./*.egg-info')

setup(name='vizigrep',
      version='1.3',
      packages=['vizigrep', 'vizigrep.guiapp'],
      cmdclass={'clean': CleanCommand},
      package_data={'vizigrep': ['ui/*']},

      # These files go to the right location when we run via debuild. However,
      # When we run ./setup.py install manually then their install locations are
      # relative to the module installation folder:
      # /usr/local/lib/python2.7/dist-packages/vizigrep-*/share/
      data_files=[
          ('share/applications', ['vizigrep.desktop']),
          ('share/vizigrep', ['vizigrep.svg']),
          ('share/doc/vizigrep', ['changelog']),
      ],

      entry_points={
          'gui_scripts': [
              'vizigrep = vizigrep.main:main'
          ]
      },
      zip_safe=False,
      include_package_data=True,
      )
      
# Create MANIFEST.in, as described here:
# https://wiki.python.org/moin/Distutils/Tutorial
