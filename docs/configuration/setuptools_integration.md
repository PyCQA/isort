# Setuptools integration

Upon installation, isort enables a `setuptools` command that checks
Python files declared by your project.

Running `python setup.py isort` on the command line will check the files
listed in your `py_modules` and `packages`. If any warning is found, the
command will exit with an error code:

```bash
$ python setup.py isort
```

Also, to allow users to be able to use the command without having to
install isort themselves, add isort to the setup\_requires of your
`setup()` like so:

```python
setup(
    name="project",
    packages=["project"],

    setup_requires=[
        "isort"
    ]
)
```
