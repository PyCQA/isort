Changelog
=========

### 4.3.19 - May 12, 2019 - hot fix release
- Fixed issue #942 - correctly handle pyi (Python Template Files) to match `black` output

### 4.3.18 - May 1, 2019 - hot fix release
- Fixed an issue with parsing files that contain unicode characters in Python 2
- Fixed issue #924 - Pulling in pip internals causes depreciation warning
- Fixed issue #938 - Providing a way to filter explicitly passed in files via configuration settings (`--filter-files`)
- Improved interoperability with toml configuration files

### 4.3.17 - April 7, 2019 - hot fix release
- Fixed issue #905 & #919: Import section headers behaving strangely

### 4.3.16 - March 23, 2019 - hot fix release
- Fixed issue #909 - skip and skip-glob are not enforced when using settings-path.
- Fixed issue #907 - appdirs optional requirement does not correctly specify version
- Fixed issue #902 - Too broad warning about missing toml package
- Fixed issue #778 - remove `user` from known standard library as it's no longer in any supported Python version.

### 4.3.15 - March 10, 2019 - hot fix release
- Fixed a regression with handling streaming input from pipes (Issue #895)
- Fixed handling of \x0c whitespace character (Issue #811)
- Improved CLI documentation

### 4.3.14 - March 9, 2019 - hot fix release
- Fixed a regression with */directory/*.py style patterns

### 4.3.13 - March 8, 2019 - hot fix release
- Fixed the inability to accurately determine import section when a mix of conda and virtual environments are used.
- Fixed some output being printed even when --quiet mode is enabled.
- Fixed issue #890 interoperability with PyCharm by allowing case sensitive non type grouped sorting.
- Fixed issue #889 under some circumstances isort will incorrectly add a new line at the beginning of a file.
- Fixed issue #885 many files not being skipped according to set skip settings.
- Fixed issue #842 streaming encoding improvements.

### 4.3.12 - March 6, 2019 - hot fix release
- Fix error caused when virtual environment not detected

### 4.3.11 - March 6, 2019 - hot fix release
- Fixed issue #876: confused by symlinks pointing to virtualenv gives FIRSTPARTY not THIRDPARTY
- Fixed issue #873: current version skips every file on travis
- Additional caching to reduce performance regression introduced in 4.3.5
- Improved handling of pex files and other binary Python files

### 4.3.10 - March 2, 2019 - hot fix release
- Fixed Windows incompatibilities (Issue #835)
- Fixed relative import sorting bug (Issue #417)
- Fixed "no_lines_before" to also be respected from previous empty sections.
- Fixed slow-down introduced by finders mechanism by adding a LRU cache (issue #848)
- Fixed issue #842 default encoding not-set in Python2
- Restored Windows automated testing
- Added Mac automated testing

### 4.3.9 - February 25, 2019 - hot fix release
- Fixed a bug that led to an incompatibility with black: #831

### 4.3.8 - February 25, 2019 - hot fix release
- Fixed a bug that led to the recursive option not always been available from the command line.

### 4.3.7 - February 25, 2019 - hot fix release
- Expands the finder failsafe to occur on the creation of the finder objects.

### 4.3.6 - February 24, 2019 - hot fix release
- Fixes a fatal error that occurs if a single finder throws an exception. Important as we add more finders that utilize third party libraries.

### 4.3.5 - February 24, 2019 - last Python 2.7 Maintenance Release

This is the final Python 2.x release of isort, and includes the following major changes:

Potentially Interface Breaking:
- The `-r` option for removing imports has been renamed `-rm` to avoid accidental deletions and confusion with the `-rc` recursive option.
- `__init__.py` has been removed from the default ignore list. The default ignore list is now empty - with all items needing to be explicitly ignored.
- Isort will now by default ignore .tox / venv folders in an effort to be "safe". You can disable this behaviour by setting the "--unsafe" flag, this is separate from any skip or not skip rules you may have in place.
- Isort now allows for files missing closing newlines in whitespace check
- `distutils` support has been removed to simplify setup.py

New:
- Official Python 3.7 Compatibility.
- Support for using requirements files to auto determine third-paty section if pipreqs & requirementslib are installed.
- Added support for using pyproject.toml if toml is installed.
- Added support for XDG_HOME if appdirs is installed.
- An option has been added to enable ignoring trailing comments ('ignore_comments') defaulting to False.
- Added support to enable line length sorting for only specific sections
- Added a `correctly_sorted` property on the SortsImport to enable more intuitive programmatic checking.

Fixes:
- Improved black compatibility.
- Isort will no detect files in the CWD as first-party.
- Fixed several cases where '-ns' or 'not_skip' was being incorrectly ignored.
- Fixed sorting of relative path imports ('.', '..', '...', etc).
- Fixed bugs caused by a failure to maintain order when loading iterables from config files.
- Correctly handle CPython compiled imports and others that need EXT_SUFFIX to correctly identify.
- Fixed handling of Symbolic Links to follow them when walking the path.
- Fixed handling of relative known_paths.
- Fixed lack of access to all wrap modes from the CLI.
- Fixed handling of FIFO files.
- Fixed a bug that could result in multiple imports being inserted on the same line.


### 4.3.4 - February 12, 2018 - hotfix release
- Fixed issue #671: isort is corrupting CRLF files

### 4.3.3 - Feburary 5, 2018 - hotfix release
- Fixed issue #665: Tabs turned into single spaces

### 4.3.2 - Feburary 4, 2018 - hotfix release
- Fixed issue #651: Add imports option is broken
- Fixed issue #662: An error generated by rewriting `.imports` to `. imoprts`

### 4.3.1 - Feburary 2, 2018 - hotfix release
- Fixed setup.py errors
- Fixed issue #654: Trailing comma count error
- Fixed issue #650: Wrong error message displayed

### 4.3.0 - January 31, 2018
- Fixed #557: `force_alphabetical_sort` and `force_sort_within_sections` can now be utilized together without extra new lines
- Fix case-sensitive path existence check in Mac OS X
- Added `--no-lines-before` for more granular control over section output
- Fixed #493: Unwanted conversion to Windows line endings
- Fixed #590: Import `as` mucks with alphabetical sorting
- Implemented `--version-number` to retrieve just the version number without the isort logo
- Breaking changes
    - Python 2.7+ only (dropped 2.6) allowing various code simplifications and improvements.

### 4.2.15 - June 6, 2017 - hotfix release
IMPORTANT NOTE: This will be the last release with Python 2.6 support, subsequent releases will be 2.7+ only
- Fixed certain one line imports not being successfully wrapped

### 4.2.14 - June 5, 2017 - hotfix release
- Fixed #559 & #565: Added missing standard library imports

### 4.2.13 - June 2, 2017 - hotfix release
- Fixed #553: Check only and --diff now work together again

### 4.2.12 - June 1, 2017 - hotfix release
- Fixed wheel distribution bug

### 4.2.11 - June 1, 2017 - hotfix release
- Fixed #546: Can't select y/n/c after latest update
- Fixed #545: Incorrectly moves __future__ imports above encoding comments

### 4.2.9 - June 1, 2017 - hotfix release
- Fixed #428: Check only modifies sorting
- Fixed #540: Not correctly identifying stdlib modules

### 4.2.8 - May 31, 2017
- Added `--virtual-env` switch command line option
- Added --enforce-whitespace option to go along with --check-only for more exact checks (issue #423)
- Fixed imports with a tailing '\' and no space in-between getting removed (issue #425)
- Fixed issue #299: long lines occasionally not wrapped
- Fixed issue #432: No longer add import inside class when class starts at top of file after encoding comment
- Fixed issue #440: Added missing `--use-parentheses` option to command line tool and documentation
- Fixed issue #496: import* imports now get successfully identified and reformatted instead of deleted
- Fixed issue #491: Non ending parentheses withing single line comments no longer cause formatting issues
- Fixed issue #471: Imports that wrap the maximum line length and contain comments on the last line are no longer rendered incorrectly
- Fixed issue #436: Force sort within section no longer rearranges comments
- Fixed issue #473: Force_to_top and force_sort_within_sections now work together
- Fixed issue #484 & #472: Consistent output with imports of same spelling but different case
- Fixed issue #433: No longer incorrectly add an extra new-line when comment between imports and function definition
- Fixed issue #419: Path specification for skipped paths is not Unix/Windows inter-operable.
Breaking Changes:
    - Fixed issue #511: All command line options with an underscore, have had the underscore replaced with a dash for consistency. This effects: multi-line, add-import, remove-import, force-adds, --force-single-line-imports, and length-sort.
    - Replaced the `--enforce-whitespace` option with `--ignore-whitespace` to restore original behavior of strict whitespace by default

### 4.2.5
- Fixed an issue that caused modules to inccorectly be matched as thirdparty when they simply had `src` in the leading path, even if they weren't withing $VIRTUALENV/src #414

### 4.2.4
- Fixed an issue that caused module that contained functions before doc strings, to incorrectly place imports
- Fixed regression in how `force_alphabetical_sort` was being interpretted (issue #409)
- Fixed stray print statement printing skipped files (issue #411)
- Added option for forcing imports into a single bucket: `no_sections`
- Added option for new lines between import types (from, straight): `lines_between_sections`

### 4.2.3
- Fixed a large number of priority bugs - bug fix only release

### 4.2.2
- Give an error message when isort is unable to determine where to place a module
- Allow imports to be sorted by module, independent of import_type, when `force_sort_within_sections` option is set
- Fixed an issue that caused Python files with 2 top comments not to be sorted

### 4.2.1
- Hot fix release to fix code error when skipping globs

### 4.2.0
- Added option "NOQA" Do not wrap lines, but add a noqa statement at the end
- Added support for running isort recursively, simply with a standalone `isort` command
- Added support to run isort library as a module
- Added compatibility for Python 3.5
- Fixed performance issue (#338) when running on project with lots of skipped directories
- Fixed issue #328: extra new can occasionally occur when using alphabetical-only sort
- Fixed custom sections parsing from config file (unicode string -> list)
- Updated pylama extension to the correct entry point
- Skip files even when file_contents is provided if they are explicitly in skip list
- Removed always showing isort banner, keeping it for when the version is requested, verbose is used, or show_logo setting is set.

### 4.1.2
- Fixed issue #323: Accidental default configuration change introduced

### 4.1.1
- Added support for partial file match skips (thanks to @Amwam)
- Added support for --quiet option to only show errors when running isort
- Fixed issue #316: isort added new lines incorrectly when a top-of line comment is present

### 4.1.0
- Started keeping a log of all changes between releases
- Added the isort logo to the command line interface
- Added example usage gif to README
- Implemented issue #292: skip setting now supports glob patterns
- Implemented issue #271: Add option to sort imports purely alphabetically
- Implemented issue #301: Readme is now natively in RST format, making it easier for Python tooling to pick up
- Implemented pylama isort extension
- Fixed issue #260: # encoding lines at the top of the file are now correctly supported
- Fixed issue #284: Sticky comments above first import are now supported
- Fixed issue #310: Ensure comments don't get duplicated when reformatting imports
- Fixed issue #289: Sections order not being respected
- Fixed issue #296: Made it more clear how to set arguments more then once

### 4.0.0
- Removed all external dependencies
