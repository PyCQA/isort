# Github Action

isort provides an official [Github Action][github-action-docs] that can be used as part of a CI/CD workflow to ensure a project's imports are properly sorted.
The action can be found on the [Github Actions Marketplace][python-isort].

## Usage

The `python-isort` plugin is designed to be run in combination with the [`checkout`][checkout-action] and [`setup-python`][setup-python] actions.
By default, it will run recursively from the root of the repository being linted and will exit with an error if the code is not properly sorted.

### Inputs

#### `isortVersion`

Optional. Version of `isort` to use. Defaults to latest version of `isort`.

#### `sortPaths`

Optional. List of paths to sort, relative to your project root. Defaults to `.`

#### `configuration`

Optional. `isort` configuration options to pass to the `isort` CLI. Defaults to `--check-only --diff`.

#### `requirementsFiles`

Optional. Paths to python requirements files to install before running isort.
If multiple requirements files are provided, they should be separated by a space.
If custom package installation is required, dependencies should be installed in a separate step before using this action.

!!! tip
    It is important that the project's dependencies be installed before running isort so that third-party libraries are properly sorted.

### Outputs

#### `isort-result`

Output of the `isort` CLI.

### Example usage

```yaml
name: Run isort
on:
  - push

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - uses: jamescurtin/isort-action@master
        with:
            requirementsFiles: "requirements.txt requirements-test.txt"
```

[github-action-docs]: https://docs.github.com/en/free-pro-team@latest/actions
[python-isort]: https://github.com/marketplace/actions/python-isort
[checkout-action]: https://github.com/actions/checkout
[setup-python]: https://github.com/actions/setup-python
