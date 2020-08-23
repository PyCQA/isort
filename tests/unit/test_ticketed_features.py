"""A growing set of tests designed to ensure when isort implements a feature described in a ticket
it fully works as defined in the associated ticket.
"""
from functools import partial
from io import StringIO

import pytest

import isort
from isort import Config, exceptions


def test_semicolon_ignored_for_dynamic_lines_after_import_issue_1178():
    """Test to ensure even if a semicolon is in the decorator in the line following an import
    the correct line spacing detrmination will be made.
    See: https://github.com/timothycrosley/isort/issues/1178.
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
    See: https://github.com/timothycrosley/isort/issues/1281
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
    See: https://github.com/timothycrosley/isort/issues/1228.
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
    See: https://github.com/timothycrosley/isort/issues/1335.
    """
    diff_output = StringIO()
    isort.code("import b\nimport a\n", show_diff=diff_output)
    diff_output.seek(0)
    assert "+import a" in diff_output.read()


def test_isort_warns_when_known_sections_dont_match_issue_1331():
    """Test to ensure that isort warns if there is a mismatch between sections and known_sections.
    See: https://github.com/timothycrosley/isort/issues/1331.
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
    See: https://github.com/timothycrosley/isort/issues/727.
    """
    assert isort.code("", add_imports=["from __future__ import absolute_imports"]) == ""
    assert (
        isort.code("import os", add_imports=["from __future__ import absolute_imports"])
        == """from __future__ import absolute_imports

import os
"""
    )


def test_isort_supports_shared_profiles_issue_970():
    """Test to ensure isort provides a way to use shared profiles.
    See: https://github.com/timothycrosley/isort/issues/970.
    """
    assert isort.code("import a", profile="example") == "import a\n"  # shared profile
    assert isort.code("import a", profile="black") == "import a\n"  # bundled profile
    with pytest.raises(exceptions.ProfileDoesNotExist):
        assert isort.code("import a", profile="madeupfake") == "import a\n"  # non-existent profile


def test_isort_supports_formatting_plugins_issue_1353():
    """Test to ensure isort provides a way to create and share formatting plugins.
    See: https://github.com/timothycrosley/isort/issues/1353.
    """
    assert isort.code("import a", formatter="example") == "import a\n"  # formatting plugin
    with pytest.raises(exceptions.FormattingPluginDoesNotExist):
        assert isort.code("import a", formatter="madeupfake") == "import a\n"  # non-existent plugin


def test_treating_comments_as_code_issue_1357():
    """Test to ensure isort provides a way to treat comments as code.
    See: https://github.com/timothycrosley/isort/issues/1357
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


def test_isort_literals_issue_1358():
    assert (
        isort.code(
            """
import x
import a


# isort: list
__all__ = ["b", "a", "b"]

# isort: unique-list
__all__ = ["b", "a", "b"]

# isort: tuple
__all__ = ("b", "a", "b")

# isort: unique-tuple
__all__ = ("b", "a", "b")

# isort: set
__all__ = {"b", "a", "b"}


def method():
    # isort: list
    x = ["b", "a"]


# isort: dict
y = {"z": "z", "b": "b", "b": "c"}"""
        )
        == """
import a
import x

# isort: list
__all__ = ['a', 'b', 'b']

# isort: unique-list
__all__ = ['a', 'b']

# isort: tuple
__all__ = ('a', 'b', 'b')

# isort: unique-tuple
__all__ = ('a', 'b')

# isort: set
__all__ = {'a', 'b'}


def method():
    # isort: list
    x = ['a', 'b']


# isort: dict
y = {'b': 'c', 'z': 'z'}"""
    )
    assert (
        isort.code(
            """
import x
import a


# isort: list
__all__ = ["b", "a", "b"]

# isort: unique-list
__all__ = ["b", "a", "b"]

# isort: tuple
__all__ = ("b", "a", "b")

# isort: unique-tuple
__all__ = ("b", "a", "b")

# isort: set
__all__ = {"b", "a", "b"}


def method():
    # isort: list
    x = ["b", "a"]


# isort: assignments
d = x
b = 2
a = 1

# isort: dict
y = {"z": "z", "b": "b", "b": "c"}""",
            formatter="example",
        )
        == """
import a
import x

# isort: list
__all__ = ["a", "b", "b"]

# isort: unique-list
__all__ = ["a", "b"]

# isort: tuple
__all__ = ("a", "b", "b")

# isort: unique-tuple
__all__ = ("a", "b")

# isort: set
__all__ = {"a", "b"}


def method():
    # isort: list
    x = ["a", "b"]


# isort: assignments
a = 1
b = 2
d = x

# isort: dict
y = {"b": "c", "z": "z"}"""
    )


def test_isort_allows_setting_import_types_issue_1181():
    """Test to ensure isort provides a way to set the type of imports.
    See: https://github.com/timothycrosley/isort/issues/1181
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
    See: https://github.com/timothycrosley/isort/issues/953
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
