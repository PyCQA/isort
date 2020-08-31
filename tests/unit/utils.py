import isort


def isort_test(code: str, expected_output: str = "", **config):
    """Runs isort against the given code snippet and ensures that it
    gives consistent output accross multiple runs, and if an expected_output
    is given - that it matches that.
    """
    expected_output = expected_output or code

    output = isort.code(code, **config)
    assert output == expected_output

    assert output == isort.code(output, **config)
