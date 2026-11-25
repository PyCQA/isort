# Excluding files and directories

Use [`--skip-glob`](options.md#skip-glob) to exclude paths when isort searches a
project recursively:

```console
isort . --skip-glob "docs/*" --skip-glob "*_pb2.py"
```

This skips files under `docs` and files whose names end in `_pb2.py`. Quote each
pattern so your shell passes it to isort unchanged. Repeat `--skip-glob` to
supply more than one pattern.

## Project configuration

To keep these exclusions in your project, add `skip_glob` to your
[configuration file](config_files.md). For example, in `pyproject.toml`:

```toml
[tool.isort]
skip_glob = ["docs/*", "*_pb2.py"]
```

For files under the configuration directory, isort matches the path relative
to that directory. With this configuration at the project root, `docs/*`
therefore matches paths such as `docs/example.py`.

Use [`extend_skip_glob`](options.md#extend-skip-glob), or the
`--extend-skip-glob` CLI option, to add patterns to an existing `skip_glob`
configuration.

## Pattern syntax

The patterns use Python's [`fnmatch`](https://docs.python.org/3/library/fnmatch.html)
syntax, rather than regular expressions:

- `*` matches any sequence of characters, including directory separators.
- `?` matches a single character.
- `[abc]` matches one of the listed characters, and `[!abc]` matches a character
  outside that set.

Because `*` can match directory separators, `docs/*` also matches
`docs/nested/example.py`; a separate `**` pattern is not needed for that case.

## Explicit file arguments

By default, a file passed directly on the command line is processed even if it
matches an exclusion. Add [`--filter-files`](options.md#filter-files) to apply
exclusions to those file arguments too:

```console
isort --filter-files --skip-glob "*_pb2.py" src/message_pb2.py
```

You can also enable this in the configuration file:

```toml
[tool.isort]
skip_glob = ["docs/*", "*_pb2.py"]
filter_files = true
```
