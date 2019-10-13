# HOPE 8 -- Style Guide for Hug Code

|             |                                             |
| ------------| ------------------------------------------- |
| HOPE:       | 8                                           |
| Title:      | Style Guide for Hug Code                    |
| Author(s):  | Timothy Crosley <timothy.crosley@gmail.com> |
| Status:     | Active                                      |
| Type:       | Process                                     |
| Created:    | 19-May-2019                                 |
| Updated:    | 17-August-2019                                 |

## Introduction

This document gives coding conventions for the Hug code comprising the Hug core as well as all official interfaces, extensions, and plugins for the framework.
Optionally, projects that use Hug are encouraged to follow this HOPE and link to it as a reference.

## PEP 8 Foundation

All guidelines in this document are in addition to those defined in Python's [PEP 8](https://www.python.org/dev/peps/pep-0008/) and [PEP 257](https://www.python.org/dev/peps/pep-0257/) guidelines.

## Line Length

Too short of lines discourage descriptive variable names where they otherwise make sense.
Too long of lines reduce overall readability and make it hard to compare 2 files side by side.
There is no perfect number: but for Hug, we've decided to cap the lines at 100 characters.

## Descriptive Variable names

Naming things is hard. Hug has a few strict guidelines on the usage of variable names, which hopefully will reduce some of the guesswork:
- No one character variable names.
    - Except for x, y, and z as coordinates.
- It's not okay to override built-in functions.
    - Except for `id`. Guido himself thought that shouldn't have been moved to the system module. It's too commonly used, and alternatives feel very artificial.
- Avoid Acronyms, Abbreviations, or any other short forms - unless they are almost universally understand.

## Adding new modules

New modules added to the a project that follows the HOPE-8 standard should all live directly within the base `PROJECT_NAME/` directory without nesting. If the modules are meant only for internal use within the project, they should be prefixed with a leading underscore. For example, def _internal_function. Modules should contain a docstring at the top that gives a general explanation of the purpose and then restates the project's use of the MIT license.
There should be a `tests/test_$MODULE_NAME.py` file created to correspond to every new module that contains test coverage for the module. Ideally, tests should be 1:1 (one test object per code object, one test method per code method) to the extent cleanly possible.

## Automated Code Cleaners

All code submitted to Hug should be formatted using Black and isort.
Black should be run with the line length set to 100, and isort with Black compatible settings in place.

## Automated Code Linting

All code submitted to hug should run through the following tools:

- Black and isort verification.
- Flake8
   - flake8-bugbear
- Bandit
- pep8-naming
- vulture
- safety
