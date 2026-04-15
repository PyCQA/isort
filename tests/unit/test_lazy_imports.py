from isort import Config, parse

from .utils import isort_test


class TestParsing:
    """Verify that ``parse.file_contents`` correctly identifies lazy imports."""

    def test_lazy_straight_import_is_stored_in_lazy_straight_bucket(self):
        result = parse.file_contents("lazy import ast\n", Config())
        assert "ast" in result.imports["STDLIB"]["lazy_straight"]
        assert "ast" not in result.imports["STDLIB"]["straight"]

    def test_lazy_from_import_is_stored_in_lazy_from_bucket(self):
        result = parse.file_contents("lazy from dataclasses import dataclass\n", Config())
        assert "dataclasses" in result.imports["STDLIB"]["lazy_from"]
        assert "dataclasses" not in result.imports["STDLIB"]["from"]

    def test_eager_imports_are_stored_in_regular_buckets(self):
        result = parse.file_contents("import os\nfrom pathlib import Path\n", Config())
        assert "os" in result.imports["STDLIB"]["straight"]
        assert "pathlib" in result.imports["STDLIB"]["from"]

    def test_lazy_imports_are_placed_in_correct_section(self):
        """Lazy imports must be placed in the same section as their eager counterparts."""
        result = parse.file_contents(
            "lazy import ast\nlazy import requests\n",
            Config(known_third_party=["requests"]),
        )
        assert "ast" in result.imports["STDLIB"]["lazy_straight"]
        assert "requests" in result.imports["THIRDPARTY"]["lazy_straight"]


def test_lazy_straight_imports_come_after_eager():
    """lazy import lines follow all eager import lines within the section."""
    isort_test("lazy import ast\nimport os\n", "import os\nlazy import ast\n")


def test_lazy_from_imports_come_after_eager():
    """lazy from ... import lines follow all eager import lines within the section."""
    isort_test(
        "lazy from pathlib import Path\nfrom collections import defaultdict\n",
        "from collections import defaultdict\nlazy from pathlib import Path\n",
    )


def test_lazy_straight_sorted_alphabetically():
    """Multiple lazy straight imports are sorted alphabetically."""
    isort_test("lazy import shutil\nlazy import ast\n", "lazy import ast\nlazy import shutil\n")


def test_lazy_from_sorted_alphabetically():
    """Multiple lazy from imports are sorted alphabetically by module name."""
    isort_test(
        "lazy from pathlib import Path\nlazy from dataclasses import dataclass\n",
        "lazy from dataclasses import dataclass\nlazy from pathlib import Path\n",
    )


def test_ruff_reference_example():
    """Reproduce the canonical example from the ruff issue tracker.

    See https://github.com/astral-sh/ruff/issues/21305.
    """
    unsorted = (
        "lazy from dataclasses import dataclass\n"
        "import json\n"
        "import os\n"
        "import subprocess\n"
        "from collections import defaultdict\n"
        "from pathlib import Path\n"
        "from typing import Final\n"
        "lazy import ast\n"
        "lazy import shutil\n"
    )
    expected = (
        "import json\n"
        "import os\n"
        "import subprocess\n"
        "from collections import defaultdict\n"
        "from pathlib import Path\n"
        "from typing import Final\n"
        "lazy import ast\n"
        "lazy import shutil\n"
        "lazy from dataclasses import dataclass\n"
    )
    isort_test(unsorted, expected)


def test_lazy_imports_appear_after_eager_in_each_section_independently():
    """Each section gets its own eager-first / lazy-last grouping."""
    unsorted = "lazy import requests\nlazy import ast\nimport os\nimport requests\n"
    expected = "import os\nlazy import ast\n\nimport requests\nlazy import requests\n"
    isort_test(unsorted, expected, known_third_party=["requests"])


def test_lazy_import_with_alias():
    """``lazy import X as Y`` is supported and sorted correctly."""
    isort_test(
        "import os\nlazy import numpy as np\n",
        "import os\n\nlazy import numpy as np\n",
        known_third_party=["numpy"],
    )


def test_lazy_from_import_multiple_names():
    """``lazy from X import a, b`` is supported and names are sorted alphabetically."""
    isort_test("lazy from typing import List, Dict\n", "lazy from typing import Dict, List\n")


def test_no_sections_mode_with_lazy_imports():
    """lazy imports are supported in no_sections mode."""
    isort_test(
        "lazy import ast\nimport os\n",
        "import os\nlazy import ast\n",
        no_sections=True,
    )


def test_from_first_option_respected_for_lazy():
    """When from_first=True, lazy from imports precede lazy straight but appear after eager."""
    isort_test(
        "import pathlib\nlazy import ast\nlazy from dataclasses import dataclass\n",
        "import pathlib\nlazy from dataclasses import dataclass\nlazy import ast\n",
        from_first=True,
    )


def test_force_sort_within_sections_applies_to_lazy():
    """force_sort_within_sections toggles lazy import ordering behavior."""
    isort_test(
        "lazy import zlib\nlazy from ast import parse\n",
        "lazy import zlib\nlazy from ast import parse\n",
        force_sort_within_sections=False,
    )
    isort_test(
        "lazy import zlib\nlazy from ast import parse\n",
        "lazy from ast import parse\nlazy import zlib\n",
        force_sort_within_sections=True,
    )
