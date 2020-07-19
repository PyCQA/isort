# isort Project Official Release Policy

isort has moved from being a simple hobby project for individuals to sort imports in their Python files
to an essential part of the CI/CD pipeline for large companies and significant Open Source projects.
Due to this evolution, it is now of increased importance that isort maintains a level of quality, predictability, and consistency
that gives projects big and small confidence to depend on it.

## Formatting guarantees

With isort 5.1.0, the isort Project guarantees that formatting will stay the same for the options given in accordance to its test suite for the duration of all major releases. This means projects can safely use isort > 5.1.0 < 6.0.0
without worrying about major formatting changes disrupting their Project.

## Packaging guarantees

Starting with the 5.0.0 release isort includes the following project guarantees to help guide development:

- isort will never have dependencies, optional, required, or otherwise.
- isort will always act the same independent to the Python environment it is installed in.

## Versioning

isort follows the [Semantic Versioning 2.0.0 specification](https://semver.org/spec/v2.0.0.html) meaning it has three numerical version parts with distinct rules
`MAJOR.MINOR.PATCH`.

### Patch Releases x.x.1

Within the isort Project, patch releases are really meant solely to fix bugs and minor oversights.
Patch releases should *never* drastically change formatting, even if it's for the better.

### Minor Releases x.1.x

Minor changes can contain new backward-incompatible features, and of particular note can include bug fixes
that result in intentional formatting changes - but they should still never be too large in scope.
API backward compatibility should strictly be maintained.

### Major Releases 1.x.x

Major releases are the only place where backward-incompatible changes or substantial formatting changes can occur.
Because these kind of changes are likely to break projects that utilize isort, either as a formatter or library,
isort must do the following:

- Release a release candidate with at least 2 weeks for bugs to be reported and fixed.
- Keep releasing follow up release candidates until there are no or few bugs reported.
- Provide an upgrade guide that helps users work around any backward-incompatible changes.
- Provide a detailed changelog of all changes.
- Where possible, warn and point to the upgrade guide instead of breaking when options are removed.
