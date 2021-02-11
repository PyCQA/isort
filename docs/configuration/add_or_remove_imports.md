
## Adding an import to multiple files
isort makes it easy to add an import statement across multiple files,
while being assured it's correctly placed.

To add an import to all files:

```bash
isort -a "from __future__ import print_function" *.py
```

To add an import only to files that already have imports:

```bash
isort -a "from __future__ import print_function" --append-only *.py
```


## Removing an import from multiple files

isort also makes it easy to remove an import from multiple files,
without having to be concerned with how it was originally formatted.

From the command line:

```bash
isort --rm "os.system" *.py
```
