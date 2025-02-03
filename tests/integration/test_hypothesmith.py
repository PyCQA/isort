import ast
from typing import get_type_hints

import hypothesis
import libcst
from hypothesis import strategies as st
from hypothesmith import from_grammar, from_node

import isort


def _as_config(kw) -> isort.Config:
    if "wrap_length" in kw and "line_length" in kw:
        kw["wrap_length"], kw["line_length"] = sorted([kw["wrap_length"], kw["line_length"]])
    try:
        return isort.Config(**kw)
    except ValueError:
        kw["wrap_length"] = 0
        return isort.Config(**kw)


def _record_targets(code: str, prefix: str = "") -> str:
    # target larger inputs - the Hypothesis engine will do a multi-objective
    # hill-climbing search using these scores to generate 'better' examples.
    nodes = list(ast.walk(ast.parse(code)))
    import_nodes = [n for n in nodes if isinstance(n, (ast.Import, ast.ImportFrom))]
    uniq_nodes = {type(n) for n in nodes}
    for value, label in [
        (len(import_nodes), "total number of import nodes"),
        (len(uniq_nodes), "number of unique ast node types"),
    ]:
        hypothesis.target(float(value), label=prefix + label)
    return code


def configs(**force_strategies: st.SearchStrategy) -> st.SearchStrategy:
    """Generate arbitrary Config objects."""
    skip = {
        "line_ending",
        "sections",
        "known_future_library",
        "forced_separate",
        "lines_before_imports",
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


@hypothesis.example("import A\nimportA\r\n\n", isort.Config(), False)
@hypothesis.given(
    source_code=st.lists(
        from_grammar(auto_target=False)
        | from_node(auto_target=False)
        | from_node(libcst.Import, auto_target=False)
        | from_node(libcst.ImportFrom, auto_target=False),
        min_size=1,
        max_size=10,
    ).map("\n".join),
    config=st.builds(isort.Config),
    disregard_skip=st.booleans(),
)
@hypothesis.seed(235738473415671197623909623354096762459)
@hypothesis.settings(
    suppress_health_check=[hypothesis.HealthCheck.too_slow, hypothesis.HealthCheck.filter_too_much]
)
def test_isort_is_idempotent(source_code: str, config: isort.Config, disregard_skip: bool) -> None:
    # NOTE: if this test finds a bug, please notify @Zac-HD so that it can be added to the
    #       Hypothesmith trophy case.  This really helps with research impact evaluations!
    _record_targets(source_code)
    result = isort.code(source_code, config=config, disregard_skip=disregard_skip)
    assert result == isort.code(result, config=config, disregard_skip=disregard_skip)
