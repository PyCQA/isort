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
- Fixed issue #316: isort added new lines incorrectly when a top-of line comment is present
