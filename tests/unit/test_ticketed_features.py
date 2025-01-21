"""A growing set of tests designed to ensure when isort implements a feature described in a ticket
it fully works as defined in the associated ticket.
"""

import warnings
from functools import partial
from io import StringIO

import pytest

import isort
from isort import Config, exceptions


def test_semicolon_ignored_for_dynamic_lines_after_import_issue_1178():
    """Test to ensure even if a semicolon is in the decorator in the line following an import
    the correct line spacing determination will be made.
    See: https://github.com/pycqa/isort/issues/1178.
    """
    assert isort.check_code(
        """
import pytest


@pytest.mark.skip(';')
def test_thing(): pass
""",
        show_diff=True,
    )


def test_isort_automatically_removes_duplicate_aliases_issue_1193():
    """Test to ensure isort can automatically remove duplicate aliases.
    See: https://github.com/pycqa/isort/issues/1281
    """
    assert isort.check_code("from urllib import parse as parse\n", show_diff=True)
    assert (
        isort.code("from urllib import parse as parse", remove_redundant_aliases=True)
        == "from urllib import parse\n"
    )
    assert isort.check_code("import os as os\n", show_diff=True)
    assert isort.code("import os as os", remove_redundant_aliases=True) == "import os\n"


def test_isort_enables_floating_imports_to_top_of_module_issue_1228():
    """Test to ensure isort will allow floating all non-indented imports to the top of a file.
    See: https://github.com/pycqa/isort/issues/1228.
    """
    assert (
        isort.code(
            """
import os


def my_function_1():
    pass

import sys

def my_function_2():
    pass
""",
            float_to_top=True,
        )
        == """
import os
import sys


def my_function_1():
    pass


def my_function_2():
    pass
"""
    )

    assert (
        isort.code(
            """
import os


def my_function_1():
    pass

# isort: split
import sys

def my_function_2():
    pass
""",
            float_to_top=True,
        )
        == """
import os


def my_function_1():
    pass

# isort: split
import sys


def my_function_2():
    pass
"""
    )

    assert (
        isort.code(
            """
import os


def my_function_1():
    pass

# isort: off
import b
import a
def y():
    pass

# isort: on
import b

def my_function_2():
    pass

import a
""",
            float_to_top=True,
        )
        == """
import os


def my_function_1():
    pass

# isort: off
import b
import a
def y():
    pass

# isort: on
import a
import b


def my_function_2():
    pass
"""
    )


def test_isort_provides_official_api_for_diff_output_issue_1335():
    """Test to ensure isort API for diff capturing allows capturing diff without sys.stdout.
    See: https://github.com/pycqa/isort/issues/1335.
    """
    diff_output = StringIO()
    isort.code("import b\nimport a\n", show_diff=diff_output)
    diff_output.seek(0)
    assert "+import a" in diff_output.read()


def test_isort_warns_when_known_sections_dont_match_issue_1331():
    """Test to ensure that isort warns if there is a mismatch between sections and known_sections.
    See: https://github.com/pycqa/isort/issues/1331.
    """
    assert (
        isort.place_module(
            "bot_core",
            config=Config(
                known_robotlocomotion_upstream=["bot_core"],
                sections=["ROBOTLOCOMOTION_UPSTREAM", "THIRDPARTY"],
            ),
        )
        == "ROBOTLOCOMOTION_UPSTREAM"
    )
    with pytest.warns(UserWarning):
        assert (
            isort.place_module(
                "bot_core",
                config=Config(
                    known_robotlocomotion_upstream=["bot_core"],
                    sections=["ROBOTLOOMOTION_UPSTREAM", "THIRDPARTY"],
                ),
            )
            == "THIRDPARTY"
        )
    with pytest.warns(UserWarning):
        assert (
            isort.place_module(
                "bot_core", config=Config(known_robotlocomotion_upstream=["bot_core"])
            )
            == "THIRDPARTY"
        )


def test_isort_supports_append_only_imports_issue_727():
    """Test to ensure isort provides a way to only add imports as an append.
    See: https://github.com/pycqa/isort/issues/727.
    """
    assert isort.code("", add_imports=["from __future__ import absolute_imports"]) == ""
    assert (
        isort.code("import os", add_imports=["from __future__ import absolute_imports"])
        == """from __future__ import absolute_imports

import os
"""
    )

    # issue 1838: don't append in middle of class
    assert isort.check_code(
        '''class C:
    """a

    """
    # comment
''',
        append_only=True,
        add_imports=["from __future__ import annotations"],
        show_diff=True,
    )


def test_isort_supports_shared_profiles_issue_970():
    """Test to ensure isort provides a way to use shared profiles.
    See: https://github.com/pycqa/isort/issues/970.
    """
    assert isort.code("import a", profile="example") == "import a\n"  # shared profile
    assert isort.code("import a", profile="black") == "import a\n"  # bundled profile
    with pytest.raises(exceptions.ProfileDoesNotExist):
        assert isort.code("import a", profile="madeupfake") == "import a\n"  # non-existent profile


def test_treating_comments_as_code_issue_1357():
    """Test to ensure isort provides a way to treat comments as code.
    See: https://github.com/pycqa/isort/issues/1357
    """
    assert (
        isort.code(
            """# %%
import numpy as np
np.array([1,2,3])

# %%
import pandas as pd
pd.Series([1,2,3])

# %%
# This is a comment on the second import
import pandas as pd
pd.Series([4,5,6])""",
            treat_comments_as_code=["# comment1", "# %%"],
        )
        == """# %%
import numpy as np

np.array([1,2,3])

# %%
import pandas as pd

pd.Series([1,2,3])

# %%
# This is a comment on the second import
import pandas as pd

pd.Series([4,5,6])
"""
    )
    assert (
        isort.code(
            """# %%
import numpy as np
np.array([1,2,3])

# %%
import pandas as pd
pd.Series([1,2,3])

# %%
# This is a comment on the second import
import pandas as pd
pd.Series([4,5,6])""",
            treat_comments_as_code=["# comment1", "# %%"],
            float_to_top=True,
        )
        == """# %%
import numpy as np
# This is a comment on the second import
import pandas as pd

np.array([1,2,3])

# %%
pd.Series([1,2,3])

# %%
pd.Series([4,5,6])
"""
    )
    assert (
        isort.code(
            """# %%
import numpy as np
np.array([1,2,3])

# %%
import pandas as pd
pd.Series([1,2,3])

# %%
# This is a comment on the second import
import pandas as pd
pd.Series([4,5,6])""",
            treat_all_comments_as_code=True,
        )
        == """# %%
import numpy as np

np.array([1,2,3])

# %%
import pandas as pd

pd.Series([1,2,3])

# %%
# This is a comment on the second import
import pandas as pd

pd.Series([4,5,6])
"""
    )
    assert (
        isort.code(
            """import b

# these are special imports that have to do with installing X plugin
import c
import a
""",
            treat_all_comments_as_code=True,
        )
        == """import b

# these are special imports that have to do with installing X plugin
import a
import c
"""
    )


def test_isort_allows_setting_import_types_issue_1181():
    """Test to ensure isort provides a way to set the type of imports.
    See: https://github.com/pycqa/isort/issues/1181
    """
    assert isort.code("from x import AA, Big, variable") == "from x import AA, Big, variable\n"
    assert (
        isort.code("from x import AA, Big, variable", constants=["variable"])
        == "from x import AA, variable, Big\n"
    )
    assert (
        isort.code("from x import AA, Big, variable", variables=["AA"])
        == "from x import Big, AA, variable\n"
    )
    assert (
        isort.code(
            "from x import AA, Big, variable",
            constants=["Big"],
            variables=["AA"],
            classes=["variable"],
        )
        == "from x import Big, variable, AA\n"
    )


def test_isort_enables_deduping_section_headers_issue_953():
    """isort should provide a way to only have identical import headings show up once.
    See: https://github.com/pycqa/isort/issues/953
    """
    isort_code = partial(
        isort.code,
        config=Config(
            import_heading_firstparty="Local imports.",
            import_heading_localfolder="Local imports.",
            dedup_headings=True,
            known_first_party=["isort"],
        ),
    )

    assert (
        isort_code("from . import something")
        == """# Local imports.
from . import something
"""
    )
    assert (
        isort_code(
            """from isort import y

from . import something"""
        )
        == """# Local imports.
from isort import y

from . import something
"""
    )
    assert isort_code("import os") == "import os\n"


def test_isort_doesnt_remove_as_imports_when_combine_star_issue_1380():
    """Test to ensure isort will not remove as imports along side other imports
    when requested to combine star imports together.
    See: https://github.com/PyCQA/isort/issues/1380
    """
    test_input = """
from a import a
from a import *
from a import b
from a import b as y
from a import c
"""
    assert (
        isort.code(
            test_input,
            combine_star=True,
        )
        == isort.code(test_input, combine_star=True, force_single_line=True)
        == isort.code(
            test_input,
            combine_star=True,
            force_single_line=True,
            combine_as_imports=True,
        )
        == """
from a import *
from a import b as y
"""
    )


def test_isort_support_custom_groups_above_stdlib_that_contain_stdlib_modules_issue_1407():
    """Test to ensure it is possible to declare custom groups above standard library that include
    modules from the standard library.
    See: https://github.com/PyCQA/isort/issues/1407
    """
    assert isort.check_code(
        """
from __future__ import annotations
from typing import *

from pathlib import Path
""",
        known_typing=["typing"],
        sections=["FUTURE", "TYPING", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"],
        no_lines_before=["TYPING"],
        show_diff=True,
    )


def test_isort_intelligently_places_noqa_comments_issue_1456():
    assert isort.check_code(
        """
from my.horribly.long.import.line.that.just.keeps.on.going.and.going.and.going import (  # noqa
    my_symbol,
)
""",
        force_single_line=True,
        show_diff=True,
        multi_line_output=3,
        include_trailing_comma=True,
        force_grid_wrap=0,
        use_parentheses=True,
        line_length=79,
    )

    assert isort.check_code(
        """
from my.horribly.long.import.line.that.just.keeps.on.going.and.going.and.going import (
    my_symbol,
)
""",
        force_single_line=True,
        show_diff=True,
        multi_line_output=3,
        include_trailing_comma=True,
        force_grid_wrap=0,
        use_parentheses=True,
        line_length=79,
    )

    assert isort.check_code(
        """
from my.horribly.long.import.line.that.just.keeps.on.going.and.going.and.going import (  # noqa
    my_symbol
)
""",
        force_single_line=True,
        use_parentheses=True,
        multi_line_output=3,
        line_length=79,
        show_diff=True,
    )

    assert isort.check_code(
        """
from my.horribly.long.import.line.that.just.keeps.on.going.and.going.and.going import (
    my_symbol
)
""",
        force_single_line=True,
        use_parentheses=True,
        multi_line_output=3,
        line_length=79,
        show_diff=True,
    )

    # see: https://github.com/PyCQA/isort/issues/1415
    assert isort.check_code(
        "from dials.test.algorithms.spot_prediction."
        "test_scan_static_reflection_predictor import (  # noqa: F401\n"
        "    data as static_test,\n)\n",
        profile="black",
        show_diff=True,
    )


def test_isort_respects_quiet_from_sort_file_api_see_1461(capsys, tmpdir):
    """Test to ensure isort respects the quiet API parameter when passed in via the API.
    See: https://github.com/PyCQA/isort/issues/1461.
    """
    settings_file = tmpdir.join(".isort.cfg")
    custom_settings_file = tmpdir.join(".custom.isort.cfg")
    tmp_file = tmpdir.join("file.py")
    tmp_file.write("import b\nimport a\n")
    isort.file(tmp_file)

    out, error = capsys.readouterr()
    assert not error
    assert "Fixing" in out

    # When passed in directly as a setting override
    tmp_file.write("import b\nimport a\n")
    isort.file(tmp_file, quiet=True)
    out, error = capsys.readouterr()
    assert not error
    assert not out

    # Present in an automatically loaded configuration file
    settings_file.write(
        """
[isort]
quiet = true
"""
    )
    tmp_file.write("import b\nimport a\n")
    isort.file(tmp_file)
    out, error = capsys.readouterr()
    assert not error
    assert not out

    # In a custom configuration file
    settings_file.write(
        """
[isort]
quiet = false
"""
    )
    custom_settings_file.write(
        """
[isort]
quiet = true
"""
    )
    tmp_file.write("import b\nimport a\n")
    isort.file(tmp_file, settings_file=str(custom_settings_file))
    out, error = capsys.readouterr()
    assert not error
    assert not out

    # Reused configuration object
    custom_config = Config(settings_file=str(custom_settings_file))
    isort.file(tmp_file, config=custom_config)
    out, error = capsys.readouterr()
    assert not error
    assert not out


def test_isort_should_warn_on_empty_custom_config_issue_1433(tmpdir):
    """Feedback should be provided when a user provides a custom settings file that has no
    discoverable configuration.
    See: https://github.com/PyCQA/isort/issues/1433
    """
    settings_file = tmpdir.join(".custom.cfg")
    settings_file.write(
        """
[settings]
quiet = true
"""
    )
    with pytest.warns(UserWarning):
        assert not Config(settings_file=str(settings_file)).quiet

    settings_file.write(
        """
[isort]
quiet = true
"""
    )
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert Config(settings_file=str(settings_file)).quiet


def test_float_to_top_should_respect_existing_newlines_between_imports_issue_1502():
    """When a file has an existing top of file import block before code but after comments
    isort's float to top feature should respect the existing spacing between the top file comment
    and the import statements.
    See: https://github.com/PyCQA/isort/issues/1502
    """
    assert isort.check_code(
        """#!/bin/bash
'''My comment'''

import a

x = 1
""",
        float_to_top=True,
        show_diff=True,
    )
    assert isort.check_code(
        """#!/bin/bash
'''My comment'''


import a

x = 1
""",
        float_to_top=True,
        show_diff=True,
    )
    assert (
        isort.code(
            """#!/bin/bash
'''My comment'''


import a

x = 1
""",
            float_to_top=True,
            add_imports=["import b"],
        )
        == """#!/bin/bash
'''My comment'''


import a
import b

x = 1
"""
    )

    assert (
        isort.code(
            """#!/bin/bash
'''My comment'''


def my_function():
    pass


import a
""",
            float_to_top=True,
        )
        == """#!/bin/bash
'''My comment'''
import a


def my_function():
    pass
"""
    )

    assert (
        isort.code(
            """#!/bin/bash
'''My comment'''


def my_function():
    pass
""",
            add_imports=["import os"],
            float_to_top=True,
        )
        == """#!/bin/bash
'''My comment'''
import os


def my_function():
    pass
"""
    )


def test_api_to_allow_custom_diff_and_output_stream_1583(capsys, tmpdir):
    """isort should provide a way from the Python API to process an existing
    file and output to a stream the new version of that file, as well as a diff
    to a different stream.
    See: https://github.com/PyCQA/isort/issues/1583
    """
    tmp_file = tmpdir.join("file.py")
    tmp_file.write("import b\nimport a\n")

    isort_diff = StringIO()
    isort_output = StringIO()

    isort.file(tmp_file, show_diff=isort_diff, output=isort_output)

    _, error = capsys.readouterr()
    assert not error

    isort_diff.seek(0)
    isort_diff_content = isort_diff.read()
    assert "+import a" in isort_diff_content
    assert " import b" in isort_diff_content
    assert "-import a" in isort_diff_content

    isort_output.seek(0)
    assert isort_output.read().splitlines() == ["import a", "import b"]

    # should still work with no diff produced
    tmp_file2 = tmpdir.join("file2.py")
    tmp_file2.write("import a\nimport b\n")

    isort_diff2 = StringIO()
    isort_output2 = StringIO()

    isort.file(tmp_file2, show_diff=isort_diff2, output=isort_output2)

    _, error = capsys.readouterr()
    assert not error

    isort_diff2.seek(0)
    assert not isort_diff2.read()


def test_autofix_mixed_indent_imports_1575():
    """isort should automatically fix import statements that are sent in
    with incorrect mixed indentation.
    See: https://github.com/PyCQA/isort/issues/1575
    """
    assert (
        isort.code(
            """
import os
  import os
  """
        )
        == """
import os
"""
    )
    assert (
        isort.code(
            """
def one():
    import os
import os
    """
        )
        == """
def one():
    import os

import os
"""
    )
    assert (
        isort.code(
            """
import os
    import os
        import os
    import os
import os
"""
        )
        == """
import os
"""
    )


def test_indented_import_headings_issue_1604():
    """Test to ensure it is possible to toggle import headings on indented import sections
    See: https://github.com/PyCQA/isort/issues/1604
    """
    assert (
        isort.code(
            """
import numpy as np


def function():
    import numpy as np
""",
            import_heading_thirdparty="External imports",
        )
        == """
# External imports
import numpy as np


def function():
    # External imports
    import numpy as np
"""
    )
    assert (
        isort.code(
            """
import numpy as np


def function():
    import numpy as np
""",
            import_heading_thirdparty="External imports",
            indented_import_headings=False,
        )
        == """
# External imports
import numpy as np


def function():
    import numpy as np
"""
    )


def test_isort_auto_detects_and_ignores_invalid_from_imports_issue_1688():
    """isort should automatically detect and ignore incorrectly written from import statements
    see: https://github.com/PyCQA/isort/issues/1688
    """
    assert (
        isort.code(
            """
from package1 import alright
from package2 imprt and_its_gone
from package3 import also_ok
"""
        )
        == """
from package1 import alright

from package2 imprt and_its_gone
from package3 import also_ok
"""
    )


def test_isort_allows_reversing_sort_order_issue_1645():
    """isort allows reversing the sort order for those who prefer Z or longer imports first.
    see: https://github.com/PyCQA/isort/issues/1688
    """
    assert (
        isort.code(
            """
from xxx import (
    g,
    hi,
    def,
    abcd,
)
""",
            profile="black",
            reverse_sort=True,
            length_sort=True,
            line_length=20,
        )
        == """
from xxx import (
    abcd,
    def,
    hi,
    g,
)
"""
    )


def test_isort_can_push_star_imports_above_others_issue_1504():
    """isort should provide a way to push star imports above other imports to avoid explicit
    imports from being overwritten.
    see: https://github.com/PyCQA/isort/issues/1504
    """
    assert (
        (
            isort.code(
                """
from ._bar import Any, All, Not
from ._foo import a, *
""",
                star_first=True,
            )
        )
        == """
from ._foo import *
from ._foo import a
from ._bar import All, Any, Not
"""
    )


def test_isort_can_combine_reverse_sort_with_force_sort_within_sections_issue_1726():
    """isort should support reversing import order even with force sort within sections turned on.
    See: https://github.com/PyCQA/isort/issues/1726
    """
    assert (
        isort.code(
            """
import blaaa
from bl4aaaaaaaaaaaaaaaa import r
import blaaaaaaaaaaaa
import bla
import blaaaaaaa
from bl1aaaaaaaaaaaaaa import this_is_1
from bl2aaaaaaa import THIIIIIIIIIIIISS_is_2
from bl3aaaaaa import less
""",
            length_sort=True,
            reverse_sort=True,
            force_sort_within_sections=True,
        )
        == """
from bl2aaaaaaa import THIIIIIIIIIIIISS_is_2
from bl1aaaaaaaaaaaaaa import this_is_1
from bl4aaaaaaaaaaaaaaaa import r
from bl3aaaaaa import less
import blaaaaaaaaaaaa
import blaaaaaaa
import blaaa
import bla
"""
    )


def test_isort_can_turn_off_import_adds_with_action_comment_issue_1737():
    assert (
        isort.code(
            """
import os
""",
            add_imports=[
                "from __future__ import absolute_imports",
                "from __future__ import annotations",
            ],
        )
        == """
from __future__ import absolute_imports, annotations

import os
"""
    )

    assert isort.check_code(
        """
# isort: dont-add-imports
import os
""",
        show_diff=True,
        add_imports=[
            "from __future__ import absolute_imports",
            "from __future__ import annotations",
        ],
    )

    assert (
        isort.code(
            """
# isort: dont-add-import: from __future__ import annotations
import os
""",
            add_imports=[
                "from __future__ import absolute_imports",
                "from __future__ import annotations",
            ],
        )
        == """
# isort: dont-add-import: from __future__ import annotations
from __future__ import absolute_imports

import os
"""
    )


def test_sort_configurable_sort_issue_1732() -> None:
    """Test support for pluggable isort sort functions."""
    test_input = (
        "from bob2.apples2 import aardvark as aardvark2\n"
        "from bob.apples import aardvark \n"
        "import module9\n"
        "import module10\n"
        "import module200\n"
    )
    assert isort.code(test_input, sort_order="native") == (
        "import module10\n"
        "import module200\n"
        "import module9\n"
        "from bob.apples import aardvark\n"
        "from bob2.apples2 import aardvark as aardvark2\n"
    )
    assert (
        isort.code(test_input, sort_order="natural")
        == isort.code(test_input)
        == (
            "import module9\n"
            "import module10\n"
            "import module200\n"
            "from bob2.apples2 import aardvark as aardvark2\n"
            "from bob.apples import aardvark\n"
        )
    )
    assert (
        isort.code(test_input, sort_order="natural_plus")
        == isort.code(test_input)
        == (
            "import module9\n"
            "import module10\n"
            "import module200\n"
            "from bob2.apples2 import aardvark as aardvark2\n"
            "from bob.apples import aardvark\n"
        )
    )
    with pytest.raises(exceptions.SortingFunctionDoesNotExist):
        isort.code(test_input, sort_order="round")


def test_cython_pure_python_imports_2062():
    """Test to ensure an import form a cython.cimports remains import, not cimport.
    See: https://github.com/pycqa/isort/issues/2062.
    """
    assert isort.check_code(
        """
import cython
from cython.cimports.libc import math


def use_libc_math():
    return math.ceil(5.5)
""",
        show_diff=True,
    )
