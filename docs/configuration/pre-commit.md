Using isort with pre-commit
========

isort provides official support for [pre-commit](https://pre-commit.com/).

### isort pre-commit step

To use isort's official pre-commit integration add the following config:

```
  - repo: https://github.com/pycqa/isort
    rev: 5.6.3
    hooks:
      - id: isort
        name: isort (python)
      - id: isort
        name: isort (cython)
        types: [cython]
      - id: isort
        name: isort (pyi)
        types: [pyi]
```

under the `repos` section of your projects `.pre-commit-config.yaml` file.

### seed-isort-config

Older versions of isort used a lot of magic to determine import placement, that could easily break when running on CI/CD.
To fix this, a utilitiy called `seed-isort-config` was created. Since isort 5 however, the project has drastically improved its placement
logic and ensured a good level of consistency across environments.
If you have a step in your pre-commit config called `seed-isort-config` or similar, it is highly recommend that you remove this.
It is guaranteed to slow things down, and can conflict with isort's own module placement logic.
