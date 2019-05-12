#!/usr/bin/env python

from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(name='isort',
      version='4.3.19',
      description='A Python utility / library to sort Python imports.',
      long_description=readme,
      author='Timothy Crosley',
      author_email='timothy.crosley@gmail.com',
      url='https://github.com/timothycrosley/isort',
      license="MIT",
      entry_points={
        'console_scripts': [
            'isort = isort.main:main',
        ],
        'distutils.commands': ['isort = isort.main:ISortCommand'],
        'pylama.linter': ['isort = isort.pylama_isort:Linter'],
      },
      packages=['isort'],
      extras_require={
          'pipfile': ['pipreqs', 'requirementslib'],
          'pyproject': ['toml'],
          'requirements': ['pipreqs', 'pip-api'],
          'xdg_home': ['appdirs>=1.4.0'],
      },
      install_requires=[
          'futures; python_version < "3.2"',
          'backports.functools_lru_cache; python_version < "3.2"',
      ],
      python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
      keywords='Refactor, Python, Python2, Python3, Refactoring, Imports, Sort, Clean',
      classifiers=['Development Status :: 6 - Mature',
                   'Intended Audience :: Developers',
                   'Natural Language :: English',
                   'Environment :: Console',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: Implementation :: CPython',
                   'Programming Language :: Python :: Implementation :: PyPy',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Utilities'])
