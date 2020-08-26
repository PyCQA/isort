#!/usr/bin/env python3
import asyncio
import sys
from getpass import getpass
from pathlib import Path
from typing import Dict

import httpx
import hug

IGNORED_AUTHOR_LOGINS = {"deepsource-autofix[bot]"}

REPO = "pycqa/isort"
GITHUB_API_CONTRIBUTORS = f"https://api.github.com/repos/{REPO}/contributors"
GITHUB_USER_CONTRIBUTIONS = f"https://github.com/{REPO}/commits?author="
GITHUB_USER_TYPE = "User"
USER_DELIMITER = "-" * 80
PER_PAGE = 100

_ACK_FILE = Path(__file__).parent.parent / "docs" / "contributing" / "4.-acknowledgements.md"
ACKNOWLEDGEMENTS = _ACK_FILE.read_text().lower()


def _user_info(user: Dict[str, str], verbose=False) -> str:
    login = "@" + user["login"]
    name = user.get("name")
    display_name = f"{name} ({login})" if name else login
    user_info = f"- {display_name}"
    if verbose:
        contributions = f"  {GITHUB_USER_CONTRIBUTIONS}{user['login']}"
        user_info += "\n" + contributions
    return user_info


@hug.cli()
async def main():
    auth = (input("Github Username: "), getpass())
    async with httpx.AsyncClient() as client:
        page = 0
        results = []
        contributors = []
        while not page or len(results) == PER_PAGE:
            page += 1
            response = await client.get(
                f"{GITHUB_API_CONTRIBUTORS}?per_page={PER_PAGE}&page={page}", auth=auth
            )
            results = response.json()
            contributors.extend(
                (
                    contributor
                    for contributor in results
                    if contributor["type"] == GITHUB_USER_TYPE
                    and contributor["login"] not in IGNORED_AUTHOR_LOGINS
                    and f"@{contributor['login'].lower()}" not in ACKNOWLEDGEMENTS
                )
            )

        unacknowledged_users = await asyncio.gather(
            *(client.get(contributor["url"], auth=auth) for contributor in contributors)
        )
        unacknowledged_users = [request.json() for request in unacknowledged_users]

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
    main.interface.cli()
