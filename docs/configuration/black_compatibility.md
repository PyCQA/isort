![isort loves black](https://raw.githubusercontent.com/pycqa/isort/develop/art/isort_loves_black.png)

Compatibility with black
========

Compatibility with black is very important to the isort project and comes baked in starting with version 5.
All that's required to use isort alongside black is to set the isort profile to "black".

## Using a config file (such as .isort.cfg)

For projects that officially use both isort and black, we recommend setting the black profile in a config file at the root of your project's repository.
This way independent to how users call isort (pre-commit, CLI, or editor integration) the black profile will automatically be applied.

For instance, your _pyproject.toml_ file would look something like

```ini
[tool.isort]
profile = "black"
multi_line_output = 3
```

Read More about supported [config files](https://pycqa.github.io/isort/docs/configuration/config_files/).

## CLI

To use the profile option when calling isort directly from the commandline simply add the --profile black argument: `isort --profile black`.

A demo of how this would look like in your _.travis.yml_

```yaml
language: python
python:
  - "3.6"
  - "3.7"
  - "3.8"

install:
  - pip install -r requirements-dev.txt
  - pip install isort black
  - pip install coveralls
script:
  - pytest my-package
  - isort --profile black my-package
  - black --check --diff my-package
after_success:
  - coveralls

```

See [built-in profiles](https://pycqa.github.io/isort/docs/configuration/profiles/) for more profiles.

## Integration with pre-commit

You can also set the profile directly when integrating isort within pre-commit.

```yaml
- repo: https://github.com/pycqa/isort
    rev: 5.6.4
    hooks:
      - id: isort
        args: ["--profile", "black", "--filter-files"]
```

