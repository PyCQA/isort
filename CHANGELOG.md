Changelog
=========

### 4.0.0
- Removed all external dependencies

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

### 4.1.1
- Added support for partial file match skips (thanks to @Amwam)
- Added support for --quiet option to only show errors when running isort
- Fixed issue #316: isort added new lines incorrectly when a top-of line comment is present

### 4.1.2
- Fixed issue #323: Accidental default configuration change introduced

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

### 4.2.1
- Hot fix release to fix code error when skipping globs

### 4.2.2
- Give an error message when isort is unable to determine where to place a module
- Allow imports to be sorted by module, independent of import_type, when `force_sort_within_sections` option is set
- Fixed an issue that caused Python files with 2 top comments not to be sorted

### 4.2.3
- Fixed a large number of priority bugs - bug fix only release

### 4.2.4
- Fixed an issue that caused module that contained functions before doc strings, to incorrectly place imports
- Fixed regression in how `force_alphabetical_sort` was being interpretted (issue #409)
- Fixed stray print statement printing skipped files (issue #411)
- Added option for forcing imports into a single bucket: `no_sections`
- Added option for new lines between import types (from, straight): `lines_between_sections`
