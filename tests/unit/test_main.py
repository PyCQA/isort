import json
import subprocess
from datetime import datetime
from io import BytesIO, TextIOWrapper

import pytest
from hypothesis import given
from hypothesis import strategies as st

from isort import main
from isort._version import __version__
from isort.exceptions import InvalidSettingsPath
from isort.settings import DEFAULT_CONFIG, Config
from isort.wrap_modes import WrapModes

# This test code was written by the `hypothesis.extra.ghostwriter` module
# and is provided under the Creative Commons Zero public domain dedication.


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


def test_iter_source_code(tmpdir):
    tmp_file = tmpdir.join("file.py")
    tmp_file.write("import os, sys\n")
    assert tuple(main.iter_source_code((tmp_file,), DEFAULT_CONFIG, [], [])) == (tmp_file,)


def test_sort_imports(tmpdir):
    tmp_file = tmpdir.join("file.py")
    tmp_file.write("import os, sys\n")
    assert main.sort_imports(str(tmp_file), DEFAULT_CONFIG, check=True).incorrectly_sorted
    main.sort_imports(str(tmp_file), DEFAULT_CONFIG)
    assert not main.sort_imports(str(tmp_file), DEFAULT_CONFIG, check=True).incorrectly_sorted

    skip_config = Config(skip=["file.py"])
    assert main.sort_imports(
        str(tmp_file), config=skip_config, check=True, disregard_skip=False
    ).skipped
    assert main.sort_imports(str(tmp_file), config=skip_config, disregard_skip=False).skipped


def test_sort_imports_error_handling(tmpdir, mocker, capsys):
    tmp_file = tmpdir.join("file.py")
    tmp_file.write("import os, sys\n")
    mocker.patch("isort.core.process").side_effect = IndexError("Example unhandled exception")
    with pytest.raises(IndexError):
        main.sort_imports(str(tmp_file), DEFAULT_CONFIG, check=True).incorrectly_sorted

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
    main.main([str(tmpdir), "--skip", "skip.py", "--check"])

    # without filter options passed in should successfully sort files
    main.main([str(python_file), str(should_skip), "--verbose", "--atomic"])

    # Should raise a system exit if all passed path is broken
    with pytest.raises(SystemExit):
        main.main(["not-exist", "--check-only"])

    # Should not raise system exit if any of passed path is not broken
    main.main([str(python_file), "not-exist", "--verbose", "--check-only"])
    out, error = capsys.readouterr()
    assert "Broken" in out

    # should respect gitignore if requested.
    out, error = capsys.readouterr()  # clear sysoutput before tests
    subprocess.run(["git", "init", str(tmpdir)])
    main.main([str(python_file), "--skip-gitignore", "--filter-files"])
    out, error = capsys.readouterr()
    assert "Skipped" not in out
    tmpdir.join(".gitignore").write("has_imports.py")
    main.main([str(python_file)])
    out, error = capsys.readouterr()
    assert "Skipped" not in out
    main.main([str(python_file), "--skip-gitignore", "--filter-files"])
    out, error = capsys.readouterr()
    assert "Skipped" in out

    # warnings should be displayed if old flags are used
    with pytest.warns(UserWarning):
        main.main([str(python_file), "--recursive", "-fss"])

    # warnings should be displayed when streaming input is provided with old flags as well
    with pytest.warns(UserWarning):
        main.main(["-sp", str(config_file), "-"], stdin=input_content)


def test_unsupported_encodings(tmpdir, capsys):
    tmp_file = tmpdir.join("file.py")
    # fmt: off
    tmp_file.write(
        u'''
# [syntax-error]\
# -*- coding: IBO-8859-1 -*-
""" check correct unknown encoding declaration
"""
__revision__ = 'יייי'
'''
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

    main.main([str(tmp_file), str(normal_file)])
    out, error = capsys.readouterr()

    assert not error


def test_isort_command():
    """Ensure ISortCommand got registered, otherwise setuptools error must have occurred"""
    assert main.ISortCommand
