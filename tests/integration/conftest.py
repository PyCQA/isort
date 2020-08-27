import isort
from hypothesis import strategies as st
from typing import get_type_hints


def _as_config(kw) -> isort.Config:
    if "wrap_length" in kw and "line_length" in kw:
        kw["wrap_length"], kw["line_length"] = sorted([kw["wrap_length"], kw["line_length"]])
    try:
        return isort.Config(**kw)
    except ValueError:
        kw["wrap_length"] = 0
        return isort.Config(**kw)


def configs(**force_strategies: st.SearchStrategy) -> st.SearchStrategy[isort.Config]:
    """Generate arbitrary Config objects."""
    skip = {
        "line_ending",
        "sections",
        "known_future_library",
        "forced_separate",
        "lines_after_imports",
        "lines_between_sections",
        "lines_between_types",
        "sources",
        "virtual_env",
        "conda_env",
        "directory",
        "formatter",
        "formatting_function",
    }
    inferred_kwargs = {
        k: st.from_type(v)
        for k, v in get_type_hints(isort.settings._Config).items()
        if k not in skip
    }
    specific = {
        "line_length": st.integers(0, 200),
        "wrap_length": st.integers(0, 200),
        "indent": st.integers(0, 20).map(lambda n: n * " "),
        "default_section": st.sampled_from(sorted(isort.settings.KNOWN_SECTION_MAPPING)),
        "force_grid_wrap": st.integers(0, 20),
        "profile": st.sampled_from(sorted(isort.settings.profiles)),
        "py_version": st.sampled_from(("auto",) + isort.settings.VALID_PY_TARGETS),
    }
    kwargs = {**inferred_kwargs, **specific, **force_strategies}
    return st.fixed_dictionaries({}, optional=kwargs).map(_as_config)


st.register_type_strategy(isort.Config, configs())
