# Shared Profiles

As well as the [built in
profiles](https://pycqa.github.io/isort/docs/configuration/profiles.html), you
can define and share your own profiles.

All that's required is to create a Python package that exposes an entry point to
a dictionary exposing profile settings under `isort.profiles`. An example is
available [within the `isort`
repo](https://github.com/PyCQA/isort/tree/main/example_shared_isort_profile)

### Example `.isort.cfg`

```
[options.entry_points]
isort.profiles =
    shared_profile=my_module:PROFILE
```
