Changelog
=========
### 4.3.0 - In progress
- Fixed #557: `force_alphabetical_sort` and `force_sort_within_sections` can now be utilized together without extra new lines
- Fix case-sensitive path existence check in Mac OS X
- Added `--no-lines-before` for more granular control over section output
- Fixed #493: Unwanted conversion to Windows line endings 
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
