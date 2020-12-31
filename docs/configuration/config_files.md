Supported Config Files
========

isort supports various standard config formats to allow customizations to be integrated into any project quickly.
When applying configurations, isort looks for the closest supported config file, in the order files are listed below.
You can manually specify the settings file or path by setting `--settings-path` from the command-line. Otherwise, isort will
traverse up to 25 parent directories until it finds a suitable config file.
Note that isort will not leave a git or Mercurial repository (checking for a `.git` or `.hg` directory).
As soon as it finds a file, it stops looking. The config file search is done relative to the current directory if `isort .`
or a file stream is passed in, or relative to the first path passed in if multiple paths are passed in.
isort **never** merges config files together due to the confusion it can cause.

!!! tip
    You can always introspect the configuration settings isort determined, and find out which config file it picked up, by running `isort . --show-config`



## .isort.cfg **[preferred format]**

The first place isort will look for settings is in dedicated .isort.cfg files.
The advantage of using this kind of config file, is that it is explicitly for isort and follows a well understood format.
The downside, is that it means one more config file in your project when you may already have several polluting your file hierarchy.

An example a config from the isort project itself:

```ini
[settings]
profile=hug
src_paths=isort,test
```

## pyproject.toml **[preferred format]**

The second place isort will look, and an equally excellent choice to place your configuration, is within a pyproject.toml file.
The advantage of using this config file, is that it is quickly becoming a standard place to configure all Python tools.
This means other developers will know to look here and you will keep your projects root nice and tidy.
The only disadvantage is that other tools you use might not yet support this format, negating the cleanliness.

```toml
[tool.isort]
profile = "hug"
src_paths = ["isort", "test"]
```

## setup.cfg

`setup.cfg` can be thought of as the precursor to `pyproject.toml`. While isort and newer tools are increasingly moving to pyproject.toml, if you rely on many tools that
use this standard it can be a natural fit to put your isort config there as well.


```ini
[isort]
profile=hug
src_paths=isort,test
```

## tox.ini

[tox](https://tox.readthedocs.io/en/latest/) is a tool commonly used in the Python community to specify multiple testing environments.
Because isort verification is commonly ran as a testing step, some prefer to place the isort config inside of the tox.ini file.

```ini
[isort]
```

## .editorconfig

Finally, isort will look for a `.editorconfig` configuration with settings for Python source files. [EditorConfig](https://editorconfig.org/) is a project to enable specifying a configuration for text editing behaviour once, allowing multiple command line tools and text editors to pick it up. Since isort cares about a lot of the same settings as a text-editor (like line-length) it makes sense for it to look within these files
as well.

```
root = true

[*.py]
profile = hug
indent_style = space
indent_size = 4
skip = build,.tox,venv
src_paths=isort,test
```

## Custom config files

Optionally, you can also create a config file with a custom name, or directly point isort to a config file that falls lower in the priority order, by using [--settings-file](https://pycqa.github.io/isort/docs/configuration/options/#settings-path).
This can be useful, for instance, if you want to have one configuration for `.py` files and another for `.pyx` - while keeping the config files at the root of your repository.

!!! tip
    Custom config files should place their configuration options inside an `[isort]` section and never a generic `[settings]` section. This is because isort can't know for sure
    how other tools are utilizing the config file.
