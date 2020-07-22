#!/usr/bin/env python3
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Union

import requests

IGNORED_AUTHOR_LOGINS = {"deepsource-autofix[bot]"}

GITHUB_USER_PATTERN = re.compile(r"@(?P<login>([a-z\d]+-)*[a-z\d]+)")
REQUESTS_TIMEOUT = (60, 60)
REPO = "timothycrosley/isort"
GITHUB_API_CONTRIBUTORS = f"https://api.github.com/repos/{REPO}/contributors"
GITHUB_USER_CONTRIBUTIONS = f"https://github.com/{REPO}/commits?author="
USER_DELIMITER = "-" * 80


def _acknowledged_logins() -> Set[str]:
    project_root = Path(__file__).parent.parent
    acknowledgments_file = project_root / "docs" / "contributing" / "4.-acknowledgements.md"
    markdown_text = acknowledgments_file.read_text()
    logins = {match.group("login") for match in re.finditer(GITHUB_USER_PATTERN, markdown_text)}
    return logins


def _request_json(url: str) -> Any:
    r = requests.get(url, timeout=REQUESTS_TIMEOUT)
    r.raise_for_status()
    return r.json()


_fetch_author_logins = partial(_request_json, GITHUB_API_CONTRIBUTORS)
_fetch_user = _request_json


def _fetch_users(urls: Iterable[str]) -> Iterable[Dict[str, Any]]:
    with ThreadPoolExecutor() as executor:
        return executor.map(_fetch_user, urls)


def _user_info(user: Dict[str, str], verbose=False) -> str:
    login = "@" + user["login"]
    name = user.get("name")
    display_name = f"{name} ({login})" if name else login
    user_info = f"- {display_name}"
    if verbose:
        contributions = f"  {GITHUB_USER_CONTRIBUTIONS}{user['login']}"
        user_info += "\n" + contributions
    return user_info


def main():
    acknowledged_logins = _acknowledged_logins()
    authors = (a for a in _fetch_author_logins() if a["login"] not in IGNORED_AUTHOR_LOGINS)

    unacknowledged_author_urls = (
        author["url"] for author in authors if author["login"] not in acknowledged_logins
    )
    unacknowledged_users = list(_fetch_users(unacknowledged_author_urls))

    if not unacknowledged_users:
        sys.exit()

    print("Found unacknowledged authors:")
    print()

    for user in unacknowledged_users:
        print(_user_info(user, verbose=True))
        print(USER_DELIMITER)

    print()
    print("Printing again for easy inclusion in Markdown file:")
    print()
    for user in unacknowledged_users:
        print(_user_info(user))

    sys.exit(1)


if __name__ == "__main__":
    main()
