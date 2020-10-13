Compatibility with black
========

black and isort sometimes don't agree on some rules. Although you can configure isort to behave nicely with black.


#Basic compatibility

Use the profile option while using isort, `isort --profile black`.

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

#Integration with pre-commit

isort can be easily used with your pre-commit hooks.

```yaml
- repo: https://github.com/pycqa/isort
    rev: 5.6.4
    hooks:
      - id: isort
        args: ["--profile", "black"]
```

#Using a config file (.isort.cfg)

The easiest way to configure black with isort is to use a config file.

```ini
[tool.isort]
profile = "black"
multi_line_output = 3
```

Read More about supported [config files](https://pycqa.github.io/isort/docs/configuration/config_files/).