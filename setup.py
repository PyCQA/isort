#!/usr/bin/env python

from distutils.core import setup

setup(name='isort',
      version='1.2.3',
      description='A Python utility / library to sort Python imports.',
      author='Timothy Crosley',
      author_email='timothy.crosley@gmail.com',
      url='https://github.com/timothycrosley/isort',
      download_url='https://github.com/timothycrosley/isort/blob/master'
                   '/dist/isort-1.2.3.tar.gz?raw=true',
      license="MIT",
      scripts=['scripts/isort'],
      packages=['isort'],
      requires=['pies', 'natsort'],
      install_requires=['pies>=1.0.3', 'natsort>=3.0.0'])
