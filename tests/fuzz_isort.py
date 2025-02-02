#!/usr/bin/python3
import sys
import io
import atheris


with atheris.instrument_imports():
    import isort
    from isort.exceptions import ExistingSyntaxErrors


def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)
    try:
        isort.api.check_code_string(fdp.ConsumeUnicodeNoSurrogates(
            fdp.ConsumeIntInRange(1, 1000)))
        isort.api.check_stream(io.StringIO(fdp.ConsumeUnicodeNoSurrogates(
            fdp.ConsumeIntInRange(1, 1000))))
    # exceptions caused by invalid inputs - ignore as uninteresting
    except (ExistingSyntaxErrors, ValueError):
        pass
    try:
        isort.api.sort_code_string(fdp.ConsumeUnicodeNoSurrogates(
            fdp.ConsumeIntInRange(1, 1000)))
        isort.api.sort_stream(io.StringIO(fdp.ConsumeUnicodeNoSurrogates(
            fdp.ConsumeIntInRange(1, 1000))),
                          io.StringIO(fdp.ConsumeUnicodeNoSurrogates(
            fdp.ConsumeIntInRange(1, 1000))))
    # exceptions caused by invalid inputs - ignore as uninteresting
    except (ExistingSyntaxErrors, ValueError):
        pass
    try:
        isort.api.place_module(fdp.ConsumeUnicodeNoSurrogates(
            fdp.ConsumeIntInRange(1, 1000)))
        isort.api.place_module_with_reason(fdp.ConsumeUnicodeNoSurrogates(
            fdp.ConsumeIntInRange(1, 1000)))
    # exceptions caused by invalid inputs - ignore as uninteresting
    except (ValueError, OSError):
        pass
    isort.api.find_imports_in_stream(io.StringIO(fdp.ConsumeUnicodeNoSurrogates(
        fdp.ConsumeIntInRange(1, 1000))))
    isort.api.find_imports_in_code(fdp.ConsumeUnicodeNoSurrogates(
        fdp.ConsumeIntInRange(1, 1000)))


atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()
