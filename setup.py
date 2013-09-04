#!/usr/bin/env python

from distutils.core import setup

setup(name='isort',
      version='1.0.0',
      description='A Python utility / library to sort Python imports.',
      author='Timothy Crosley',
      author_email='timothy.crosley@gmail.com',
      url='https://github.com/timothycrosley/isort',
      download_url='https://github.com/timothycrosley/isort/blob/master'
                   '/dist/isort-1.0.0.tar.gz?raw=true',
      license="GNU GPLv2",
      scripts=['scripts/isort'],
      packages=['isort'],
      requires=['pies'],
      install_requires=['pies>=1.0.2'])
