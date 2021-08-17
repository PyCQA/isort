from io import BytesIO, StringIO, TextIOWrapper

import isort


class UnseekableTextIOWrapper(TextIOWrapper):
    def seek(self, *args, **kwargs):
        raise ValueError("underlying stream is not seekable")


class UnreadableStream(StringIO):
    def readable(self, *args, **kwargs) -> bool:
        return False


def as_stream(text: str) -> UnseekableTextIOWrapper:
    return UnseekableTextIOWrapper(BytesIO(text.encode("utf8")))


def isort_test(code: str, expected_output: str = "", **config):
    """Runs isort against the given code snippet and ensures that it
    gives consistent output across multiple runs, and if an expected_output
    is given - that it matches that.
    """
    expected_output = expected_output or code

    output = isort.code(code, **config)
    assert output == expected_output

    assert output == isort.code(output, **config)
