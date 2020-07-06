"""A growing set of tests designed to ensure isort doesn't have regressions in new versions"""
import isort


def test_isort_duplicating_comments_issue_1264():
    """Ensure isort doesn't duplicate comments when force_sort_within_sections is set to `True`
    as was the case in issue #1264: https://github.com/timothycrosley/isort/issues/1264
    """
    assert isort.code("""
from homeassistant.util.logging import catch_log_exception

# Loading the config flow file will register...
from . import config_flow
""", force_sort_within_sections=True).count("# Loading the config flow file will register...") == 1
