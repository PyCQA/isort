Changelog
=========

NOTE: isort follows the [semver](https://semver.org/) versioning standard.
Find out more about isort's release policy [here](https://pycqa.github.io/isort/docs/major_releases/release_policy).

### 5.11.3 December 16 2022

  - Fixed #2007: settings for py3.11 (#2040) @staticdev
  - Fixed #2038: packaging pypoetry (#2042) @staticdev
  - Docs: renable portray (#2043) @timothycrosley
  - Ci: add minimum GitHub token permissions for workflows (#1969) @varunsh-coder
  - Ci: general CI improvements (#2041) @staticdev
  - Ci: add release workflow (#2026) @staticdev

### 5.11.2 December 12 2022

  - Hotfix #2034: isort --version is not accurate on 5.11.x releases (#2034) @gschaffner

### 5.11.1 December 12 2022

  - Hotfix #2031: only call `colorama.init` if `colorama` is available (#2032) @tomaarsen

### 5.11.0 December 12 2022

  - Added official support for Python 3.11 (#1996, #2008, #2011) @staticdev
  - Dropped support for Python 3.6 (#2019) @barrelful
  - Fixed problematic tests (#2021, #2022) @staticdev
  - Fixed #1960: Rich compatibility (#1961) @ofek
  - Fixed #1945, #1986: Python 4.0 upper bound dependency resolving issues @staticdev
  - Fixed Pyodide CDN URL (#1991) @andersk
  - Docs: clarify description of use_parentheses (#1941) @mgedmin
  - Fixed #1976: `black` compatibility for `.pyi` files @XuehaiPan
  - Implemented #1683: magic trailing comma option (#1876) @legau
  - Add missing space in unrecoverable exception message (#1933) @andersk
  - Fixed #1895: skip-gitignore: use allow list, not deny list @bmalehorn
  - Fixed #1917: infinite loop for unmatched parenthesis (#1919) @anirudnits
  - Docs: shared profiles (#1896) @matthewhughes934
  - Fixed build-backend values in the example plugins (#1892) @mgorny
  - Remove reference to jamescurtin/isort-action (#1885) @AndrewLane
  - Split long cython import lines (#1931) @davidcollins001
  - Update plone profile: copy of `black`, plus three settings. (#1926) @mauritsvanrees
  - Fixed #1815, #1862: Add a command-line flag to sort all re-exports (#1863) @parafoxia
  - Fixed #1854: `lines_before_imports` appending lines after comments (#1861) @legau
  - Remove redundant `multi_line_output = 3` from "Compatibility with black" (#1858) @jdufresne
  - Add tox config example (#1856) @umonaca
  - Docs: add examples for frozenset and tuple settings (#1822) @sgaist
  - Docs: add multiple config documentation (#1850) @anirudnits

### 5.10.1 November 8 2021
  - Fixed #1819: Occasional inconsistency with multiple src paths.
  - Fixed #1840: skip_file ignored when on the first docstring line

### 5.10.0 November 3 2021
  - Implemented #1796: Switch to `tomli` for pyproject.toml configuration loader.
  - Fixed #1801: CLI bug (--exend-skip-glob, overrides instead of extending).
  - Fixed #1802: respect PATH customization in nested calls to git.
  - Fixed #1838: Append only with certain code snippets incorrectly adds imports.
  - Added official support for Python 3.10

#### Potentially breaking changes:
  - Fixed #1785: `_ast` module incorrectly excluded from stdlib definition.

### 5.9.3 July 28 2021
  - Improved text of skipped file message to mention gitignore feature.
  - Made all exceptions pickleable.
  - Fixed #1779: Pylama integration ignores pylama specific isort config overrides.
  - Fixed #1781: `--from-first` CLI flag shouldn't take any arguments.
  - Fixed #1792: Sorting literals sometimes ignored when placed on first few lines of file.
  - Fixed #1777: extend_skip is not honored wit a git submodule when skip_gitignore=true.

### 5.9.2 July 8th 2021
  - Improved behavior of `isort --check --atomic` against Cython files.
  - Fixed #1769: Future imports added below assignments when no other imports present.
  - Fixed #1772: skip-gitignore will check files not in the git repository.
  - Fixed #1762: in some cases when skip-gitignore is set, isort fails to skip any files.
  - Fixed #1767: Encoding issues surfacing when invalid characters set in `__init__.py` files during placement.
  - Fixed #1771: Improved handling of skips against named streamed in content.

### 5.9.1 June 21st 2021 [hotfix]
  - Fixed #1758: projects with many files and skip_ignore set can lead to a command-line overload.

### 5.9.0 June 21st 2021
  - Improved CLI startup time.
  - Implemented #1697: Provisional support for PEP 582: skip `__pypackages__` directories by default.
  - Implemented #1705: More intuitive handling of isort:skip_file comments on streams.
  - Implemented #1737: Support for using action comments to avoid adding imports to individual files.
  - Implemented #1750: Ability to customize output format lines.
  - Implemented #1732: Support for custom sort functions.
  - Implemented #1722: Improved behavior for running isort in atomic mode over Cython source files.
  - Fixed (https://github.com/PyCQA/isort/pull/1695): added imports being added to doc string in some cases.
  - Fixed (https://github.com/PyCQA/isort/pull/1714): in rare cases line continuation combined with tabs can output invalid code.
  - Fixed (https://github.com/PyCQA/isort/pull/1726): isort ignores reverse_sort when force_sort_within_sections is true.
  - Fixed #1741: comments in hanging indent modes can lead to invalid code.
  - Fixed #1744: repeat noqa comments dropped when * import and non * imports exist from the same package.
  - Fixed #1721: repeat noqa comments on separate from lines with force-single-line set, sometimes get dropped.

#### Goal Zero (Tickets related to aspirational goal of achieving 0 regressions for remaining 5.0.0 lifespan):
  - Implemented #1394: 100% branch coverage (in addition to line coverage) enforced.
  - Implemented #1751: Strict typing enforcement (turned on mypy strict mode).

### 5.8.0 March 20th 2021
  - Fixed #1631: as import comments can in some cases be duplicated.
  - Fixed #1667: extra newline added with float-to-top, after skip, in some cases.
  - Fixed #1594: incorrect placement of noqa comments with multiple from imports.
  - Fixed #1566: in some cases different length limits for dos based line endings.
  - Implemented #1648: Export MyPY type hints.
  - Implemented #1641: Identified import statements now return runnable code.
  - Implemented #1661: Added "wemake" profile.
  - Implemented #1669: Parallel (`-j`) now defaults to number of CPU cores if no value is provided.
  - Implemented #1668: Added a safeguard against accidental usage against /.
  - Implemented #1638 / #1644: Provide a flag `--overwrite-in-place` to ensure same file handle is used after sorting.
  - Implemented #1684: Added support for extending skips with `--extend-skip` and `--extend-skip-glob`.
  - Implemented #1688: Auto identification and skipping of some invalid import statements.
  - Implemented #1645: Ability to reverse the import sorting order.
  - Implemented #1504: Added ability to push star imports to the top to avoid overriding explicitly defined imports.
  - Documented #1685: Skip doesn't support plain directory names, but skip_glob does.

### 5.7.0 December 30th 2020
  - Fixed #1612: In rare circumstances an extra comma is added after import and before comment.
  - Fixed #1593: isort encounters bug in Python 3.6.0.
  - Implemented #1596: Provide ways for extension formatting and file paths to be specified when using streaming input from CLI.
  - Implemented #1583: Ability to output and diff within a single API call to `isort.file`.
  - Implemented #1562, #1592 & #1593: Better more useful fatal error messages.
  - Implemented #1575: Support for automatically fixing mixed indentation of import sections.
  - Implemented #1582: Added a CLI option for skipping symlinks.
  - Implemented #1603: Support for disabling float_to_top from the command line.
  - Implemented #1604: Allow toggling section comments on and off for indented import sections.

### 5.6.4 October 12, 2020
  - Fixed #1556: Empty line added between imports that should be skipped.

### 5.6.3 October 11, 2020
  - Improved packaging of test files alongside source distribution (see: https://github.com/PyCQA/isort/pull/1555).

### 5.6.2 October 10, 2020
  - Fixed #1548: On rare occasions an unecessary empty line can be added when an import is marked as skipped.
  - Fixed #1542: Bug in VERTICAL_PREFIX_FROM_MODULE_IMPORT wrap mode.
  - Fixed #1552: Pylama test dependent on source layout.

#### Goal Zero: (Tickets related to aspirational goal of achieving 0 regressions for remaining 5.0.0 lifespan):
  - Zope added to integration test suite
  - Additional testing of CLI (simulate unseekable streams)

### 5.6.1 [Hotfix] October 8, 2020
  - Fixed #1546: Unstable (non-idempotent) behavior with certain src trees.

### 5.6.0 October 7, 2020
  - Implemented #1433: Provide helpful feedback in case a custom config file is specified without a configuration.
  - Implemented #1494: Default to sorting imports within `.pxd` files.
  - Implemented #1502: Improved float-to-top behavior when there is an existing import section present at top-of-file.
  - Implemented #1511: Support for easily seeing all files isort will be ran against using `isort . --show-files`.
  - Implemented #1487: Improved handling of encoding errors.
  - Improved handling of unsupported configuration option errors (see #1475).
  - Fixed #1463: Better interactive documentation for future option.
  - Fixed #1461: Quiet config option not respected by file API in some circumstances.
  - Fixed #1482: pylama integration is not working correctly out-of-the-box.
  - Fixed #1492: --check does not work with stdin source.
  - Fixed #1499: isort gets confused by single line, multi-line style comments when using float-to-top.
  - Fixed #1525: Some warnings can't be disabled with --quiet.
  - Fixed #1523: in rare cases isort can ignore direct from import if as import is also on same line.

#### Potentially breaking changes:
  - Implemented #1540: Officially support Python 3.9 stdlib imports by default.
  - Fixed #1443: Incorrect third vs first party categorization - namespace packages.
  - Fixed #1486: "Google" profile is not quite Google style.
  - Fixed "PyCharm" profile to always add 2 lines to be consistent with what PyCharm "Optimize Imports" does.

#### Goal Zero: (Tickets related to aspirational goal of achieving 0 regressions for remaining 5.0.0 lifespan):
  - Implemented #1472: Full testing of stdin CLI Options
  - Added additional branch coverage.
  - More projects added to integration test suite.

### 5.5.5 [Hotfix] October 7, 2020
  - Fixed #1539: in extremely rare cases isort 5.5.4 introduces syntax error by removing closing paren.

### 5.5.4 [Hotfix] September 29, 2020
  - Fixed #1507: in rare cases isort changes the content of multiline strings after a yield statement.
  - Fixed #1505: Support case where known_SECTION points to a section not listed in sections.

### 5.5.3 [Hotfix] September 20, 2020
  - Fixed #1488: in rare cases isort can mangle `yield from` or `raise from` statements.

### 5.5.2 [Hotfix] September 9, 2020
  - Fixed #1469: --diff option is ignored when input is from stdin.

### 5.5.1 September 4, 2020
  - Fixed #1454: Ensure indented import sections with import heading and a preceding comment don't cause import sorting loops.
  - Fixed #1453: isort error when float to top on almost empty file.
  - Fixed #1456 and #1415: noqa comment moved to where flake8 cant see it.
  - Fixed #1460: .svn missing from default ignore list.

### 5.5.0 September 3, 2020
  - Fixed #1398: isort: off comment doesn't work, if it's the top comment in the file.
  - Fixed #1395: reverse_relative setting doesn't have any effect when combined with force_sort_within_sections.
  - Fixed #1399: --skip can error in the case of projects that contain recursive symlinks.
  - Fixed #1389: ensure_newline_before_comments doesn't work if comment is at top of section and sections don't have lines between them.
  - Fixed #1396: comments in imports with ";" can keep isort from recognizing import line.
  - Fixed #1380: As imports removed when `combine_star` is set.
  - Fixed #1382: --float-to-top has no effect if no import is already at the top.
  - Fixed #1420: isort never settles on module docstring + add import.
  - Fixed #1421: Error raised when repo contains circular symlinks.
  - Fixed #1427: noqa comment is moved from star import to constant import.
  - Fixed #1444 & 1445: Incorrect placement of import additions.
  - Fixed #1447: isort5 throws error when stdin used on Windows with deprecated args.
  - Implemented #1397: Added support for specifying config file when using git hook (thanks @diseraluca!).
  - Implemented #1405: Added support for coloring diff output.
  - Implemented #1434: New multi-line grid mode without parentheses.

#### Goal Zero (Tickets related to aspirational goal of achieving 0 regressions for remaining 5.0.0 lifespan):
  - Implemented #1392: Extensive profile testing.
  - Implemented #1393: Proprety based testing applied to code snippets.
  - Implemented #1391: Create automated integration test that includes full code base of largest OpenSource isort users.

#### Potentially breaking changes:
  - Fixed #1429: --check doesn't print to stderr as the documentation says. This means if you were looking for `ERROR:` messages for files that contain incorrect imports within stdout you will now need to look in stderr.

### 5.4.2 Aug 14, 2020
  - Fixed #1383: Known other does not work anymore with .editorconfig.
  - Fixed: Regression in first known party path expansion.

### 5.4.1 [Hotfix] Aug 13, 2020
  - Fixed #1381: --combine-as loses # noqa in different circumstances.

### 5.4.0 Aug 12, 2020
  - Implemented #1373: support for length sort only of direct (AKA straight) imports.
  - Fixed #1321: --combine-as loses # noqa.
  - Fixed #1375: --dont-order-by-type CLI broken.

### 5.3.2 [Hotfix] Aug 7, 2020
  - Fixed incorrect warning code (W503->W0503).

### 5.3.1 Aug 7, 2020
  - Improve upgrade warnings to be less noisy and point to error codes for easy interoperability with Visual Studio Code (see: #1363).

### 5.3.0 Aug 4, 2020
  - Implemented ability to treat all or select comments as code (issue #1357)
  - Implemented ability to use different configs for different file extensions (issue #1162)
  - Implemented ability to specify the types of imports (issue #1181)
  - Implemented ability to dedup import headings (issue #953)
  - Added experimental support for sorting literals (issue #1358)
  - Added experimental support for sorting and deduping groupings of assignments.
  - Improved handling of deprecated single line variables for usage with Visual Studio Code (issue #1363)
  - Improved handling of mixed newline forms within same source file.
  - Improved error handling for known sections.
  - Improved API consistency, returning a boolean value for all modification API calls to indicate if changes were made.
  - Fixed #1366: spurious errors when combining skip with --gitignore.
  - Fixed #1359: --skip-gitignore does not honor ignored symlink

#### Internal Development:
  - Initial hypothesmith powered test to help catch unexpected syntax parsing and output errors (thanks @Zac-HD!)

### 5.2.2 July 30, 2020
  - Fixed #1356: return status when arguments are passed in without files or a content stream.

### 5.2.1 July 28, 2020
  - Update precommit to default to filtering files that are defined in skip.
  - Improved relative path detection for `skip` config usage.
  - Added recursive symbolic link protection.
  - Implemented #1177: Support for color output using `--color`.
  - Implemented recursive symlink detection support.

### 5.2.0 July 27, 2020
  - Implemented #1335: Official API for diff capturing.
  - Implemented #1331: Warn when sections don't match up.
  - Implemented #1261: By popular demand, `filter_files` can now be set in the config option.
  - Implemented #960: Support for respecting git ignore via "--gitignore" or "skip_gitignore=True".
  - Implemented #727: Ability to only add imports if existing imports exist.
  - Implemented #970: Support for custom sharable isort profiles.
  - Implemented #1214: Added support for git_hook lazy option (Thanks @sztamas!)
  - Implemented #941: Added an additional `multi_line_output` mode for more compact formatting (Thanks @sztamas!)
  - Implemented #1020: Option for LOCALFOLDER.
  - Implemented #1353: Added support for output formatting plugins.
  - `# isort: split` can now be used at the end of an import line.
  - Fixed #1339: Extra indent is not preserved when isort:skip is used in nested imports.
  - Fixed #1348: `--diff` works incorrectly with files that have CRLF line endings.
  - Improved code repositories usage of pylint tags (#1350).

### 5.1.4 July 19, 2020
  - Fixed issue #1333: Use of wrap_length raises an exception about it not being lower or equal to line_length.
  - Fixed issue #1330: Ensure stdout can be stubbed dynamically for `show_unified_diff` function.

### 5.1.3 July 18, 2020
  - Fixed issue #1329: Fix comments duplicated when --fass option is set.

### 5.1.2 July 17, 2020
  - Fixed issue #1219 / #1326: Comments not wrapped for long lines
  - Fixed issue #1156: Bug related to isort:skip usage followed by a multiline comment block

### 5.1.1 July 15, 2020
  - Fixed issue #1322: Occasionally two extra newlines before comment with `-n` & `--fss`.
  - Fixed issue #1189: `--diff` broken when reading from standard input.

### 5.1.0 July 14, 2020
  - isort now throws an exception if an invalid settings path is given (issue #1174).
  - Implemented support for automatic redundant alias removal (issue #1281).
  - Implemented experimental support for floating all imports to the top of a file (issue #1228)
  - Fixed #1178: support for semicolons in decorators.
  - Fixed #1315: Extra newline before comment with -n + --fss.
  - Fixed #1192: `-k` or `--keep-direct-and-as-imports` option has been deprecated as it is now always on.

#### Formatting changes implied:
  - Fixed #1280: rewrite of as imports changes the behavior of the imports.

### 5.0.9 July 11, 2020
  - Fixed #1301: Import headings in nested sections leads to check errors

### 5.0.8 July 11, 2020
  - Fixed #1277 & #1278: New line detection issues on Windows.
  - Fixed #1294: Fix bundled git hook.

### 5.0.7 July 9, 2020
  - Fixed #1306: unexpected --diff behavior.
  - Fixed #1279: Fixed NOQA comment regression.

### 5.0.6 July 8, 2020
  - Fixed #1302: comments and --trailing-comma can generate invalid code.
  - Fixed #1293: extra new line in indented imports, when immediately followed by a comment.
  - Fixed #1304: isort 5 no longer recognises `sre_parse` as a stdlib module.
  - Fixed #1300: add_imports moves comments following import section.
  - Fixed #1276: Fix a bug that creates only one line after triple quotes.

### 5.0.5 July 7, 2020
  - Fixed #1285: packaging issue with bundling tests via poetry.
  - Fixed #1284: Regression when sorting `.pyi` files from CLI using black profile.
  - Fixed #1275 & #1283: Blank line after docstring removed.
  - Fixed #1298: CLI Help out of date with isort 5.
  - Fixed #1290: Unecessary blank lines above nested imports when import comments turned on.
  - Fixed #1297: Usage of `--add-imports` alongside `--check` is broken.
  - Fixed #1289: Stream usage no longer auto picking up config file from current working directory.
  - Fixed #1296: Force_single_line setting removes immediately following comment line.
  - Fixed #1295: `ensure_newline_before_comments` doesnt work with `force_sort_within_sections`.
  - Setting not_skip will no longer immediately fail but instead give user a warning and direct
    to upgrade docs.

### 5.0.4 July 6, 2020
  - Fixed #1264: a regression with comment handling and `force_sort_within_sections` config option
  - Added warning for deprecated CLI flags and linked to upgrade guide.

### 5.0.3 - July 4, 2020
  - Fixed setup.py command incorrectly passing check=True as a configuration parameter (see: https://github.com/pycqa/isort/issues/1258)
  - Fixed missing patch version
  - Fixed issue #1253: Atomic fails when passed in not readable output stream

### 5.0.2 - July 4, 2020
  - Ensured black profile was complete, adding missing line_length definition.

### 5.0.1 - July 4, 2020
  - Fixed a runtime error in a vendored dependency (toml).

### 5.0.0 Penny - July 4, 2020
**Breaking changes:**

  - isort now requires Python 3.6+ to run but continues to support formatting on ALL versions of python including
    Python 2 code.
  - isort deprecates official support for Python 3.4, removing modules only in this release from known_standard_library:
      - user
  - Config files are no longer composed on-top of each-other. Instead the first config file found is used.
    - Since there is no longer composition negative form settings (such as --dont-skip or it's config file variant `not_skip`) are no longer required and have been removed.
  - Two-letter shortened setting names (like `ac` for `atomic`) now require two dashes to avoid ambiguity: `--ac`.
  - For consistency with other tools `-v` now is shorthand for verbose and `-V` is shorthand for version. See Issue: #1067.
  - `length_sort_{section_name}` config usage has been deprecated. Instead `length_sort_sections` list can be used to specify a list of sections that need to be length sorted.
  - `safety_excludes` and `unsafe` have been deprecated
  - Config now includes as default full set of safety directories defined by safety excludes.
  - `--recursive` option has been removed. Directories passed in are now automatically sorted recursive.
  - `--apply` option has been removed as it is the default behaviour.
  - isort now does nothing, beyond giving instructions and exiting status code 0, when ran with no arguments.
    - a new `--interactive` flag has been added to enable the old style behaviour.
  - isort now works on contiguous sections of imports, instead of one whole file at a time.
  - ~~isort now formats all nested "as" imports in the "from" form. `import x.y as a` becomes `from x import y as a`.~~ NOTE: This was undone in version 5.1.0 due to feedback it caused issues with some project conventions.
  - `keep_direct_and_as_imports` option now defaults to `True`.
  - `appdirs` is no longer supported. Unless manually specified, config should be project config only.
  - `toml` is now installed as a vendorized module, meaning pyproject.toml based config is always supported.
  - Completely new Python API, old version is removed and no longer accessible.
  - New module placement logic and module fully replaces old finders. Old approach is still available via `--old-finders`.

Internal:

  - isort now utilizes mypy and typing to filter out typing related issues before deployment.
  - isort now utilizes black internally to ensure more consistent formatting.

- profile support for common project types (black, django, google, etc)

- Much much more. There is some difficulty in fully capturing the extent of changes in this release - just because of how all encompassing the release is. See: [Github Issues](https://github.com/pycqa/isort/issues?q=is%3Aissue+is%3Aclosed) for more.

### 4.3.21 - June 25, 2019 - hot fix release
- Fixed issue #957 - Long aliases and use_parentheses generates invalid syntax

### 4.3.20 - May 14, 2019 - hot fix release
- Fixed issue #948 - Pipe redirection broken on Python2.7

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
- Isort will now detect files in the CWD as first-party.
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
