import json
import os
import pathlib
import shutil
import subprocess
from datetime import datetime

import pytest
from hypothesis import given
from hypothesis import strategies as st

from isort import main
from isort._version import __version__
from isort.exceptions import InvalidSettingsPath
from isort.settings import DEFAULT_CONFIG, Config
from .utils import as_stream
from io import BytesIO, TextIOWrapper
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    WrapModes: Any
else:
    from isort.wrap_modes import WrapModes


@given(
    file_name=st.text(),
    config=st.builds(Config),
    check=st.booleans(),
    ask_to_apply=st.booleans(),
    write_to_stdout=st.booleans(),
)
def test_fuzz_sort_imports(file_name, config, check, ask_to_apply, write_to_stdout):
    main.sort_imports(
        file_name=file_name,
        config=config,
        check=check,
        ask_to_apply=ask_to_apply,
        write_to_stdout=write_to_stdout,
    )


def test_sort_imports(tmpdir):
    tmp_file = tmpdir.join("file.py")
    tmp_file.write("import os, sys\n")
    assert main.sort_imports(str(tmp_file), DEFAULT_CONFIG, check=True).incorrectly_sorted  # type: ignore # noqa
    main.sort_imports(str(tmp_file), DEFAULT_CONFIG)
    assert not main.sort_imports(str(tmp_file), DEFAULT_CONFIG, check=True).incorrectly_sorted  # type: ignore # noqa

    skip_config = Config(skip=["file.py"])
    assert main.sort_imports(  # type: ignore
        str(tmp_file), config=skip_config, check=True, disregard_skip=False
    ).skipped
    assert main.sort_imports(str(tmp_file), config=skip_config, disregard_skip=False).skipped  # type: ignore # noqa


def test_sort_imports_error_handling(tmpdir, mocker, capsys):
    tmp_file = tmpdir.join("file.py")
    tmp_file.write("import os, sys\n")
    mocker.patch("isort.core.process").side_effect = IndexError("Example unhandled exception")
    with pytest.raises(IndexError):
        main.sort_imports(str(tmp_file), DEFAULT_CONFIG, check=True).incorrectly_sorted  # type: ignore # noqa

    out, error = capsys.readouterr()
    assert "Unrecoverable exception thrown when parsing" in error


def test_parse_args():
    assert main.parse_args([]) == {}
    assert main.parse_args(["--multi-line", "1"]) == {"multi_line_output": WrapModes.VERTICAL}
    assert main.parse_args(["--multi-line", "GRID"]) == {"multi_line_output": WrapModes.GRID}
    assert main.parse_args(["--dont-order-by-type"]) == {"order_by_type": False}
    assert main.parse_args(["--dt"]) == {"order_by_type": False}
    assert main.parse_args(["--only-sections"]) == {"only_sections": True}
    assert main.parse_args(["--os"]) == {"only_sections": True}
    assert main.parse_args(["--om"]) == {"only_modified": True}
    assert main.parse_args(["--only-modified"]) == {"only_modified": True}
    assert main.parse_args(["--csi"]) == {"combine_straight_imports": True}
    assert main.parse_args(["--combine-straight-imports"]) == {"combine_straight_imports": True}
    assert main.parse_args(["--dont-follow-links"]) == {"follow_links": False}
    assert main.parse_args(["--overwrite-in-place"]) == {"overwrite_in_place": True}
    assert main.parse_args(["--from-first"]) == {"from_first": True}
    assert main.parse_args(["--resolve-all-configs"]) == {"resolve_all_configs": True}


def test_ascii_art(capsys):
    main.main(["--version"])
    out, error = capsys.readouterr()
    assert (
        out
        == f"""
                 _                 _
                (_) ___  ___  _ __| |_
                | |/ _/ / _ \\/ '__  _/
                | |\\__ \\/\\_\\/| |  | |_
                |_|\\___/\\___/\\_/   \\_/

      isort your imports, so you don't have to.

                    VERSION {__version__}

"""
    )
    assert error == ""


def test_preconvert():
    assert main._preconvert(frozenset([1, 1, 2])) == [1, 2]
    assert main._preconvert(WrapModes.GRID) == "GRID"
    assert main._preconvert(main._preconvert) == "_preconvert"
    with pytest.raises(TypeError):
        main._preconvert(datetime.now())


def test_show_files(capsys, tmpdir):
    tmpdir.join("a.py").write("import a")
    tmpdir.join("b.py").write("import b")

    # show files should list the files isort would sort
    main.main([str(tmpdir), "--show-files"])
    out, error = capsys.readouterr()
    assert "a.py" in out
    assert "b.py" in out
    assert not error

    # can not be used for stream
    with pytest.raises(SystemExit):
        main.main(["-", "--show-files"])

    # can not be used with show-config
    with pytest.raises(SystemExit):
        main.main([str(tmpdir), "--show-files", "--show-config"])


def test_missing_default_section(tmpdir):
    config_file = tmpdir.join(".isort.cfg")
    config_file.write(
        """
[settings]
sections=MADEUP
"""
    )

    python_file = tmpdir.join("file.py")
    python_file.write("import os")

    with pytest.raises(SystemExit):
        main.main([str(python_file)])


def test_ran_against_root():
    with pytest.raises(SystemExit):
        main.main(["/"])


def test_main(capsys, tmpdir):
    base_args = [
        "-sp",
        str(tmpdir),
        "--virtual-env",
        str(tmpdir),
        "--src-path",
        str(tmpdir),
    ]
    tmpdir.mkdir(".git")

    # If nothing is passed in the quick guide is returned without erroring
    main.main([])
    out, error = capsys.readouterr()
    assert main.QUICK_GUIDE in out
    assert not error

    # If no files are passed in but arguments are the quick guide is returned, alongside an error.
    with pytest.raises(SystemExit):
        main.main(base_args)
    out, error = capsys.readouterr()
    assert main.QUICK_GUIDE in out

    # Unless the config is requested, in which case it will be returned alone as JSON
    main.main(base_args + ["--show-config"])
    out, error = capsys.readouterr()
    returned_config = json.loads(out)
    assert returned_config
    assert returned_config["virtual_env"] == str(tmpdir)

    # This should work even if settings path is not provided
    main.main(base_args[2:] + ["--show-config"])
    out, error = capsys.readouterr()
    assert json.loads(out)["virtual_env"] == str(tmpdir)

    # This should raise an error if an invalid settings path is provided
    with pytest.raises(InvalidSettingsPath):
        main.main(
            base_args[2:]
            + ["--show-config"]
            + ["--settings-path", "/random-root-folder-that-cant-exist-right?"]
        )

    # Should be able to set settings path to a file
    config_file = tmpdir.join(".isort.cfg")
    config_file.write(
        """
[settings]
profile=hug
verbose=true
"""
    )
    config_args = ["--settings-path", str(config_file)]
    main.main(
        config_args
        + ["--virtual-env", "/random-root-folder-that-cant-exist-right?"]
        + ["--show-config"]
    )
    out, error = capsys.readouterr()
    assert json.loads(out)["profile"] == "hug"

    # Should be able to stream in content to sort
    input_content = TextIOWrapper(
        BytesIO(
            b"""
import b
import a
"""
        )
    )
    main.main(config_args + ["-"], stdin=input_content)
    out, error = capsys.readouterr()
    assert (
        out
        == f"""
else-type place_module for b returned {DEFAULT_CONFIG.default_section}
else-type place_module for a returned {DEFAULT_CONFIG.default_section}
import a
import b
"""
    )

    # Should be able to stream diff
    input_content = TextIOWrapper(
        BytesIO(
            b"""
import b
import a
"""
        )
    )
    main.main(config_args + ["-", "--diff"], stdin=input_content)
    out, error = capsys.readouterr()
    assert not error
    assert "+" in out
    assert "-" in out
    assert "import a" in out
    assert "import b" in out

    # check should work with stdin

    input_content_check = TextIOWrapper(
        BytesIO(
            b"""
import b
import a
"""
        )
    )

    with pytest.raises(SystemExit):
        main.main(config_args + ["-", "--check-only"], stdin=input_content_check)
    out, error = capsys.readouterr()
    assert error == "ERROR:  Imports are incorrectly sorted and/or formatted.\n"

    # Should be able to run with just a file
    python_file = tmpdir.join("has_imports.py")
    python_file.write(
        """
import b
import a
"""
    )
    main.main([str(python_file), "--filter-files", "--verbose"])
    assert python_file.read().lstrip() == "import a\nimport b\n"

    # Add a file to skip
    should_skip = tmpdir.join("should_skip.py")
    should_skip.write("import nothing")
    main.main(
        [
            str(python_file),
            str(should_skip),
            "--filter-files",
            "--verbose",
            "--skip",
            str(should_skip),
        ]
    )

    # Should raise a system exit if check only, with broken file
    python_file.write(
        """
import b
import a
"""
    )
    with pytest.raises(SystemExit):
        main.main(
            [
                str(python_file),
                str(should_skip),
                "--filter-files",
                "--verbose",
                "--check-only",
                "--skip",
                str(should_skip),
            ]
        )

    # Should have same behavior if full directory is skipped
    with pytest.raises(SystemExit):
        main.main(
            [str(tmpdir), "--filter-files", "--verbose", "--check-only", "--skip", str(should_skip)]
        )

    # Nested files should be skipped without needing --filter-files
    nested_file = tmpdir.mkdir("nested_dir").join("skip.py")
    nested_file.write("import b;import a")
    python_file.write(
        """
import a
import b
"""
    )
    main.main([str(tmpdir), "--extend-skip", "skip.py", "--check"])

    # without filter options passed in should successfully sort files
    main.main([str(python_file), str(should_skip), "--verbose", "--atomic"])

    # Should raise a system exit if all passed path is broken
    with pytest.raises(SystemExit):
        main.main(["not-exist", "--check-only"])

    # Should not raise system exit if any of passed path is not broken
    main.main([str(python_file), "not-exist", "--verbose", "--check-only"])
    out, error = capsys.readouterr()
    assert "Broken" in out

    # warnings should be displayed if old flags are used
    with pytest.warns(UserWarning):
        main.main([str(python_file), "--recursive", "-fss"])

    # warnings should be displayed when streaming input is provided with old flags as well
    with pytest.warns(UserWarning):
        main.main(["-sp", str(config_file), "-"], stdin=input_content)


def test_isort_filename_overrides(tmpdir, capsys):
    """Tests isorts available approaches for overriding filename and extension based behavior"""
    input_text = """
import b
import a

def function():
    pass
"""

    def build_input_content():
        return as_stream(input_text)

    main.main(["-"], stdin=build_input_content())
    out, error = capsys.readouterr()
    assert not error
    assert out == (
        """
import a
import b


def function():
    pass
"""
    )

    # if file is skipped it should output unchanged.
    main.main(
        ["-", "--filename", "x.py", "--skip", "x.py", "--filter-files"],
        stdin=build_input_content(),
    )
    out, error = capsys.readouterr()
    assert not error
    assert out == (
        """
import b
import a

def function():
    pass
"""
    )

    main.main(["-", "--ext-format", "pyi"], stdin=build_input_content())
    out, error = capsys.readouterr()
    assert not error
    assert out == (
        """
import a
import b

def function():
    pass
"""
    )

    tmp_file = tmpdir.join("tmp.pyi")
    tmp_file.write_text(input_text, encoding="utf8")
    main.main(["-", "--filename", str(tmp_file)], stdin=build_input_content())
    out, error = capsys.readouterr()
    assert not error
    assert out == (
        """
import a
import b

def function():
    pass
"""
    )

    # setting a filename override when file is passed in as non-stream is not supported.
    with pytest.raises(SystemExit):
        main.main([str(tmp_file), "--filename", str(tmp_file)], stdin=build_input_content())


def test_isort_float_to_top_overrides(tmpdir, capsys):
    """Tests isorts supports overriding float to top from CLI"""
    test_input = """
import b


def function():
    pass


import a
"""
    config_file = tmpdir.join(".isort.cfg")
    config_file.write(
        """
[settings]
float_to_top=True
"""
    )
    python_file = tmpdir.join("file.py")
    python_file.write(test_input)

    main.main([str(python_file)])
    out, error = capsys.readouterr()
    assert not error
    assert "Fixing" in out
    assert python_file.read_text(encoding="utf8") == (
        """
import a
import b


def function():
    pass
"""
    )

    python_file.write(test_input)
    main.main([str(python_file), "--dont-float-to-top"])
    _, error = capsys.readouterr()
    assert not error
    assert python_file.read_text(encoding="utf8") == test_input

    with pytest.raises(SystemExit):
        main.main([str(python_file), "--float-to-top", "--dont-float-to-top"])


def test_isort_with_stdin(capsys):
    # ensures that isort sorts stdin without any flags

    input_content = as_stream(
        """
import b
import a
"""
    )

    main.main(["-"], stdin=input_content)
    out, error = capsys.readouterr()

    assert out == (
        """
import a
import b
"""
    )

    input_content_from = as_stream(
        """
import c
import b
from a import z, y, x
"""
    )

    main.main(["-"], stdin=input_content_from)
    out, error = capsys.readouterr()

    assert out == (
        """
import b
import c
from a import x, y, z
"""
    )

    # ensures that isort correctly sorts stdin with --fas flag

    input_content = as_stream(
        """
import sys
import pandas
from z import abc
from a import xyz
"""
    )

    main.main(["-", "--fas"], stdin=input_content)
    out, error = capsys.readouterr()

    assert out == (
        """
from a import xyz
from z import abc

import pandas
import sys
"""
    )

    # ensures that isort correctly sorts stdin with --fass flag

    input_content = as_stream(
        """
from a import Path, abc
"""
    )

    main.main(["-", "--fass"], stdin=input_content)
    out, error = capsys.readouterr()

    assert out == (
        """
from a import abc, Path
"""
    )

    # ensures that isort correctly sorts stdin with --ff flag

    input_content = as_stream(
        """
import b
from c import x
from a import y
"""
    )

    main.main(["-", "--ff"], stdin=input_content)
    out, error = capsys.readouterr()

    assert out == (
        """
from a import y
from c import x
import b
"""
    )

    # ensures that isort correctly sorts stdin with -fss flag

    input_content = as_stream(
        """
import b
from a import a
"""
    )

    main.main(["-", "--fss"], stdin=input_content)
    out, error = capsys.readouterr()

    assert out == (
        """
from a import a
import b
"""
    )

    input_content = as_stream(
        """
import a
from b import c
"""
    )

    main.main(["-", "--fss"], stdin=input_content)
    out, error = capsys.readouterr()

    assert out == (
        """
import a
from b import c
"""
    )

    # ensures that isort correctly sorts stdin with --ds flag

    input_content = as_stream(
        """
import sys
import pandas
import a
"""
    )

    main.main(["-", "--ds"], stdin=input_content)
    out, error = capsys.readouterr()

    assert out == (
        """
import a
import pandas
import sys
"""
    )

    # ensures that isort correctly sorts stdin with --cs flag

    input_content = as_stream(
        """
from a import b
from a import *
"""
    )

    main.main(["-", "--cs"], stdin=input_content)
    out, error = capsys.readouterr()

    assert out == (
        """
from a import *
"""
    )

    # ensures that isort correctly sorts stdin with --ca flag

    input_content = as_stream(
        """
from a import x as X
from a import y as Y
"""
    )

    main.main(["-", "--ca"], stdin=input_content)
    out, error = capsys.readouterr()

    assert out == (
        """
from a import x as X, y as Y
"""
    )

    # ensures that isort works consistently with check and ws flags

    input_content = as_stream(
        """
import os
import a
import b
"""
    )

    main.main(["-", "--check-only", "--ws"], stdin=input_content)
    out, error = capsys.readouterr()

    assert not error

    # ensures that isort works consistently with check and diff flags

    input_content = as_stream(
        """
import b
import a
"""
    )

    with pytest.raises(SystemExit):
        main.main(["-", "--check", "--diff"], stdin=input_content)
    out, error = capsys.readouterr()

    assert error
    assert "underlying stream is not seekable" not in error
    assert "underlying stream is not seekable" not in error

    # ensures that isort correctly sorts stdin with --ls flag

    input_content = as_stream(
        """
import abcdef
import x
"""
    )

    main.main(["-", "--ls"], stdin=input_content)
    out, error = capsys.readouterr()

    assert out == (
        """
import x
import abcdef
"""
    )

    # ensures that isort correctly sorts stdin with --nis flag

    input_content = as_stream(
        """
from z import b, c, a
"""
    )

    main.main(["-", "--nis"], stdin=input_content)
    out, error = capsys.readouterr()

    assert out == (
        """
from z import b, c, a
"""
    )

    # ensures that isort correctly sorts stdin with --sl flag

    input_content = as_stream(
        """
from z import b, c, a
"""
    )

    main.main(["-", "--sl"], stdin=input_content)
    out, error = capsys.readouterr()

    assert out == (
        """
from z import a
from z import b
from z import c
"""
    )

    # ensures that isort correctly sorts stdin with --top flag

    input_content = as_stream(
        """
import os
import sys
"""
    )
    main.main(["-", "--top", "sys"], stdin=input_content)
    out, error = capsys.readouterr()

    assert out == (
        """
import sys
import os
"""
    )

    # ensure that isort correctly sorts stdin with --os flag

    input_content = as_stream(
        """
import sys
import os
import z
from a import b, e, c
"""
    )
    main.main(["-", "--os"], stdin=input_content)
    out, error = capsys.readouterr()

    assert out == (
        """
import sys
import os

import z
from a import b, e, c
"""
    )

    # ensures that isort warns with deprecated flags with stdin
    input_content = as_stream(
        """
import sys
import os
"""
    )

    with pytest.warns(UserWarning):
        main.main(["-", "-ns"], stdin=input_content)

    out, error = capsys.readouterr()

    assert out == (
        """
import os
import sys
"""
    )

    input_content = as_stream(
        """
import sys
import os
"""
    )

    with pytest.warns(UserWarning):
        main.main(["-", "-k"], stdin=input_content)

    out, error = capsys.readouterr()

    assert out == (
        """
import os
import sys
"""
    )

    # ensures that only-modified flag works with stdin
    input_content = as_stream(
        """
import a
import b
"""
    )

    main.main(["-", "--verbose", "--only-modified"], stdin=input_content)
    out, error = capsys.readouterr()

    assert "else-type place_module for a returned THIRDPARTY" not in out
    assert "else-type place_module for b returned THIRDPARTY" not in out

    # ensures that combine-straight-imports flag works with stdin
    input_content = as_stream(
        """
import a
import b
"""
    )

    main.main(["-", "--combine-straight-imports"], stdin=input_content)
    out, error = capsys.readouterr()

    assert out == (
        """
import a, b
"""
    )


def test_unsupported_encodings(tmpdir, capsys):
    tmp_file = tmpdir.join("file.py")
    # fmt: off
    tmp_file.write_text(
        '''
# [syntax-error]\
# -*- coding: IBO-8859-1 -*-
""" check correct unknown encoding declaration
"""
__revision__ = 'יייי'
''',
        encoding="utf8"
    )
    # fmt: on

    # should throw an error if only unsupported encoding provided
    with pytest.raises(SystemExit):
        main.main([str(tmp_file)])
    out, error = capsys.readouterr()

    assert "No valid encodings." in error

    # should not throw an error if at least one valid encoding found
    normal_file = tmpdir.join("file1.py")
    normal_file.write("import os\nimport sys")

    main.main([str(tmp_file), str(normal_file), "--verbose"])
    out, error = capsys.readouterr()


def test_stream_skip_file(tmpdir, capsys):
    input_with_skip = """
# isort: skip_file
import b
import a
"""
    stream_with_skip = as_stream(input_with_skip)
    main.main(["-"], stdin=stream_with_skip)
    out, error = capsys.readouterr()
    assert out == input_with_skip

    input_without_skip = input_with_skip.replace("isort: skip_file", "generic comment")
    stream_without_skip = as_stream(input_without_skip)
    main.main(["-"], stdin=stream_without_skip)
    out, error = capsys.readouterr()
    assert (
        out
        == """
# generic comment
import a
import b
"""
    )

    atomic_input_without_skip = input_with_skip.replace("isort: skip_file", "generic comment")
    stream_without_skip = as_stream(atomic_input_without_skip)
    main.main(["-", "--atomic"], stdin=stream_without_skip)
    out, error = capsys.readouterr()
    assert (
        out
        == """
# generic comment
import a
import b
"""
    )


def test_only_modified_flag(tmpdir, capsys):
    # ensures there is no verbose output for correct files with only-modified flag

    file1 = tmpdir.join("file1.py")
    file1.write(
        """
import a
import b
"""
    )

    file2 = tmpdir.join("file2.py")
    file2.write(
        """
import math

import pandas as pd
"""
    )

    main.main([str(file1), str(file2), "--verbose", "--only-modified"])
    out, error = capsys.readouterr()

    assert (
        out
        == f"""
                 _                 _
                (_) ___  ___  _ __| |_
                | |/ _/ / _ \\/ '__  _/
                | |\\__ \\/\\_\\/| |  | |_
                |_|\\___/\\___/\\_/   \\_/

      isort your imports, so you don't have to.

                    VERSION {__version__}

"""
    )

    assert not error

    # ensures that verbose output is only for modified file(s) with only-modified flag

    file3 = tmpdir.join("file3.py")
    file3.write(
        """
import sys
import os
"""
    )

    main.main([str(file1), str(file2), str(file3), "--verbose", "--only-modified"])
    out, error = capsys.readouterr()

    assert "else-type place_module for sys returned STDLIB" in out
    assert "else-type place_module for os returned STDLIB" in out
    assert "else-type place_module for math returned STDLIB" not in out
    assert "else-type place_module for pandas returned THIRDPARTY" not in out

    assert not error

    # ensures that the behaviour is consistent for check flag with only-modified flag

    main.main([str(file1), str(file2), "--check-only", "--verbose", "--only-modified"])
    out, error = capsys.readouterr()

    assert (
        out
        == f"""
                 _                 _
                (_) ___  ___  _ __| |_
                | |/ _/ / _ \\/ '__  _/
                | |\\__ \\/\\_\\/| |  | |_
                |_|\\___/\\___/\\_/   \\_/

      isort your imports, so you don't have to.

                    VERSION {__version__}

"""
    )

    assert not error

    file4 = tmpdir.join("file4.py")
    file4.write(
        """
import sys
import os
"""
    )

    with pytest.raises(SystemExit):
        main.main([str(file2), str(file4), "--check-only", "--verbose", "--only-modified"])
    out, error = capsys.readouterr()

    assert "else-type place_module for sys returned STDLIB" in out
    assert "else-type place_module for os returned STDLIB" in out
    assert "else-type place_module for math returned STDLIB" not in out
    assert "else-type place_module for pandas returned THIRDPARTY" not in out


def test_identify_imports_main(tmpdir, capsys):
    file_content = "import mod2\nimport mod2\n" "a = 1\n" "import mod1\n"
    some_file = tmpdir.join("some_file.py")
    some_file.write(file_content)
    file_imports = f"{some_file}:1 import mod2\n{some_file}:4 import mod1\n"
    file_imports_with_dupes = (
        f"{some_file}:1 import mod2\n{some_file}:2 import mod2\n" f"{some_file}:4 import mod1\n"
    )

    main.identify_imports_main([str(some_file), "--unique"])
    out, error = capsys.readouterr()
    assert out.replace("\r\n", "\n") == file_imports
    assert not error

    main.identify_imports_main([str(some_file)])
    out, error = capsys.readouterr()
    assert out.replace("\r\n", "\n") == file_imports_with_dupes
    assert not error

    main.identify_imports_main(["-", "--unique"], stdin=as_stream(file_content))
    out, error = capsys.readouterr()
    assert out.replace("\r\n", "\n") == file_imports.replace(str(some_file), "")

    main.identify_imports_main(["-"], stdin=as_stream(file_content))
    out, error = capsys.readouterr()
    assert out.replace("\r\n", "\n") == file_imports_with_dupes.replace(str(some_file), "")

    main.identify_imports_main([str(tmpdir)])

    main.identify_imports_main(["-", "--packages"], stdin=as_stream(file_content))
    out, error = capsys.readouterr()
    assert len(out.split("\n")) == 6

    main.identify_imports_main(["-", "--modules"], stdin=as_stream(file_content))
    out, error = capsys.readouterr()
    assert len(out.split("\n")) == 3

    main.identify_imports_main(["-", "--attributes"], stdin=as_stream(file_content))
    out, error = capsys.readouterr()
    assert len(out.split("\n")) == 3


def test_gitignore(capsys, tmp_path: pathlib.Path):
    import_content = """
import b
import a
"""

    def main_check(args):
        try:
            main.main(args)
        except SystemExit:
            pass
        return capsys.readouterr()

    subprocess.run(["git", "init", str(tmp_path)])
    python_file = tmp_path.joinpath("has_imports.py")
    python_file.write_text(import_content)
    tmp_path.joinpath("no_imports.py").write_text("...")

    out, error = main_check([str(python_file), "--skip-gitignore", "--filter-files", "--check"])
    assert "has_imports.py" in error and "no_imports.py" not in error

    tmp_path.joinpath(".gitignore").write_text("has_imports.py")

    out, error = main_check([str(python_file), "--check"])
    assert "has_imports.py" in error and "no_imports.py" not in error

    out, error = main_check([str(python_file), "--skip-gitignore", "--filter-files", "--check"])
    assert "Skipped" in out

    # Should work with nested directories
    tmp_path.joinpath("nested_dir").mkdir()
    tmp_path.joinpath(".gitignore").write_text("nested_dir/has_imports.py")
    subfolder_file = tmp_path.joinpath("nested_dir/has_imports.py")
    subfolder_file.write_text(import_content)

    out, error = main_check([str(tmp_path), "--skip-gitignore", "--filter-files", "--check"])
    assert "has_imports.py" in error and "nested_dir/has_imports.py" not in error

    # Should work with relative path
    currentdir = os.getcwd()
    os.chdir(tmp_path)

    out, error = main_check([".", "--skip-gitignore", "--filter-files", "--check"])
    assert "has_imports.py" in error and "nested_dir/has_imports.py" not in error

    tmp_path.joinpath(".gitignore").write_text(
        """
nested_dir/has_imports.py
has_imports.py
"""
    )
    out, error = main_check([".", "--skip-gitignore", "--filter-files", "--check"])
    assert "Skipped" in out

    os.chdir(currentdir)

    # Should work with multiple git projects

    shutil.rmtree(tmp_path.joinpath(".git"))
    tmp_path.joinpath(".gitignore").unlink()

    # git_project0
    # | has_imports_ignored.py ignored
    # | has_imports.py should check
    git_project0 = tmp_path.joinpath("git_project0")
    git_project0.mkdir()
    subprocess.run(["git", "init", str(git_project0)])
    git_project0.joinpath(".gitignore").write_text("has_imports_ignored.py")
    git_project0.joinpath("has_imports_ignored.py").write_text(import_content)
    git_project0.joinpath("has_imports.py").write_text(import_content)

    # git_project1
    # | has_imports.py should check
    # | nested_dir
    #   | has_imports_ignored.py ignored
    #   | has_imports.py should check
    # | nested_dir_ignored ignored
    #   | has_imports.py ignored from folder
    git_project1 = tmp_path.joinpath("git_project1")
    git_project1.mkdir()
    subprocess.run(["git", "init", str(git_project1)])
    git_project1.joinpath(".gitignore").write_text(
        """
nested_dir/has_imports_ignored.py
nested_dir_ignored
"""
    )
    git_project1.joinpath("has_imports.py").write_text(import_content)
    nested_dir = git_project1.joinpath("nested_dir")
    nested_dir.mkdir()
    nested_dir.joinpath("has_imports.py").write_text(import_content)
    nested_dir.joinpath("has_imports_ignored.py").write_text(import_content)
    nested_ignored_dir = git_project1.joinpath("nested_dir_ignored")
    nested_ignored_dir.mkdir()
    nested_ignored_dir.joinpath("has_imports.py").write_text(import_content)

    should_check = [
        "/has_imports.py",
        "/nested_dir/has_imports.py",
        "/git_project0/has_imports.py",
        "/git_project1/has_imports.py",
        "/git_project1/nested_dir/has_imports.py",
    ]

    out, error = main_check([str(tmp_path), "--skip-gitignore", "--filter-files", "--check"])

    if os.name == "nt":
        should_check = [sc.replace("/", "\\") for sc in should_check]

    assert all(f"{str(tmp_path)}{file}" in error for file in should_check)

    out, error = main_check([str(tmp_path), "--skip-gitignore", "--filter-files"])

    assert all(f"{str(tmp_path)}{file}" in out for file in should_check)

    # Should work when git project contains symlinks

    if os.name != "nt":
        git_project0.joinpath("has_imports_ignored.py").write_text(import_content)
        git_project0.joinpath("has_imports.py").write_text(import_content)
        tmp_path.joinpath("has_imports.py").write_text(import_content)
        tmp_path.joinpath("nested_dir").joinpath("has_imports.py").write_text(import_content)
        git_project0.joinpath("ignore_link.py").symlink_to(tmp_path.joinpath("has_imports.py"))
        git_project0.joinpath("ignore_link").symlink_to(tmp_path.joinpath("nested_dir"))
        gitignore = git_project0.joinpath(".gitignore")
        gitignore.write_text(gitignore.read_text() + "ignore_link.py\nignore_link")

        out, error = main_check(
            [str(git_project0), "--skip-gitignore", "--filter-files", "--check"]
        )

        should_check = ["/git_project0/has_imports.py"]

        assert all(f"{str(tmp_path)}{file}" in error for file in should_check)

        out, error = main_check([str(git_project0), "--skip-gitignore", "--filter-files"])

        assert all(f"{str(tmp_path)}{file}" in out for file in should_check)


def test_multiple_configs(capsys, tmpdir):
    # Ensure that --resolve-all-configs flag resolves multiple configs correctly
    # and sorts files corresponding to their nearest config

    setup_cfg = """
[isort]
from_first=True
"""

    pyproject_toml = """
[tool.isort]
no_inline_sort = \"True\"
"""

    isort_cfg = """
[settings]
force_single_line=True
"""

    broken_isort_cfg = """
[iaort_confg]
force_single_line=True
"""

    dir1 = tmpdir / "subdir1"
    dir2 = tmpdir / "subdir2"
    dir3 = tmpdir / "subdir3"
    dir4 = tmpdir / "subdir4"

    dir1.mkdir()
    dir2.mkdir()
    dir3.mkdir()
    dir4.mkdir()

    setup_cfg_file = dir1 / "setup.cfg"
    setup_cfg_file.write_text(setup_cfg, "utf-8")

    pyproject_toml_file = dir2 / "pyproject.toml"
    pyproject_toml_file.write_text(pyproject_toml, "utf-8")

    isort_cfg_file = dir3 / ".isort.cfg"
    isort_cfg_file.write_text(isort_cfg, "utf-8")

    broken_isort_cfg_file = dir4 / ".isort.cfg"
    broken_isort_cfg_file.write_text(broken_isort_cfg, "utf-8")

    import_section = """
from a import y, z, x
import b
"""

    file1 = dir1 / "file1.py"
    file1.write_text(import_section, "utf-8")

    file2 = dir2 / "file2.py"
    file2.write_text(import_section, "utf-8")

    file3 = dir3 / "file3.py"
    file3.write_text(import_section, "utf-8")

    file4 = dir4 / "file4.py"
    file4.write_text(import_section, "utf-8")

    file5 = tmpdir / "file5.py"
    file5.write_text(import_section, "utf-8")

    main.main([str(tmpdir), "--resolve-all-configs", "--cr", str(tmpdir), "--verbose"])
    out, _ = capsys.readouterr()

    assert f"{str(setup_cfg_file)} used for file {str(file1)}" in out
    assert f"{str(pyproject_toml_file)} used for file {str(file2)}" in out
    assert f"{str(isort_cfg_file)} used for file {str(file3)}" in out
    assert f"default used for file {str(file4)}" in out
    assert f"default used for file {str(file5)}" in out

    assert (
        file1.read()
        == """
from a import x, y, z
import b
"""
    )

    assert (
        file2.read()
        == """
import b
from a import y, z, x
"""
    )
    assert (
        file3.read()
        == """
import b
from a import x
from a import y
from a import z
"""
    )
    assert (
        file4.read()
        == """
import b
from a import x, y, z
"""
    )

    assert (
        file5.read()
        == """
import b
from a import x, y, z
"""
    )

    # Ensure that --resolve-all-config flags works with --check

    file6 = dir1 / "file6.py"
    file6.write(
        """
import b
from a import x, y, z
    """
    )

    with pytest.raises(SystemExit):
        main.main([str(tmpdir), "--resolve-all-configs", "--cr", str(tmpdir), "--check"])

    _, err = capsys.readouterr()

    assert f"{str(file6)} Imports are incorrectly sorted and/or formatted" in err


def test_multiple_src_paths(tmpdir, capsys):
    """
    Ensure that isort has consistent behavior with multiple source paths
    """

    tests_module = tmpdir / "tests"
    app_module = tmpdir / "app"

    tests_module.mkdir()
    app_module.mkdir()

    pyproject_toml = tmpdir / "pyproject.toml"
    pyproject_toml.write_text(
        """
[tool.isort]
profile = "black"
src_paths = ["app", "tests"]
auto_identify_namespace_packages = false
""",
        "utf-8",
    )
    file = tmpdir / "file.py"
    file.write_text(
        """
from app.something import something
from tests.something import something_else
""",
        "utf-8",
    )

    for _ in range(10):  # To ensure isort has consistent results in multiple runs
        main.main([str(tmpdir), "--verbose"])
        out, _ = capsys.readouterr()

        assert (
            file.read()
            == """
from app.something import something
from tests.something import something_else
"""
        )
        assert "from-type place_module for tests.something returned FIRSTPARTY" in out
