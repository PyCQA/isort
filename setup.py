#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='isort',
      version='2.0.1',
      description='A Python utility / library to sort Python imports.',
      author='Timothy Crosley',
      author_email='timothy.crosley@gmail.com',
      url='https://github.com/timothycrosley/isort',
      download_url='https://github.com/timothycrosley/isort/archive/2.0.1.tar.gz',
      license="MIT",
      scripts=['scripts/isort'],
      packages=['isort'],
      requires=['pies', 'natsort'],
      install_requires=['pies>=1.0.3', 'natsort>=3.0.0'])
