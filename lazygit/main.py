from typing import Dict, Any
import argparse
import os
import shlex
import re
import subprocess
from lazygit.exceptions import LazyGitError
from lazygit.handlers import get_pr_handler

TOKEN = os.environ.get("LAZYGIT_ACCESS_TOKEN")

URL = "https://gitlab.com"

PROBLEM_TEMPLATE = """
## Problems:
{problems}
"""


FIX_TEMPLATE = """
## Fixes:
{fixes}
"""

NOTE_TEMPLATE = """
## Notes
{notes}
"""

FEATURE_TEMPLATE = """
## Feature:
{features}
"""

def run(cmd: str) -> str:
    return subprocess.check_output(
        shlex.split(cmd),
        stderr=subprocess.STDOUT,
    ).decode().strip()


def notify(msg: str) -> None:
    run(f'notify-send -i info "{msg}"')


def get_branch_info() -> str:
    info = run("git remote show origin")
    return info


def get_last_commit_message() -> str:
    return run("git log -1 --pretty=%s")


def push_source_branch() -> None:
    run("git push -u origin HEAD")


def get_remote_source_branch() -> str:
    # try:
    #     return run("git rev-parse --abbrev-ref --symbolic-full-name @{u}")
    # except:
    return run("git rev-parse --abbrev-ref HEAD")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--repo", help="repo url")
    parser.add_argument("-s", "--source", help="source branch")
    parser.add_argument("-t", "--target", help="target branch")
    parser.add_argument("--title", help="Title of the pr")
    parser.add_argument("-b", "--block", action="store_true", help="notes")
    parser.add_argument("-o", "--collect", help="Collect links in format")
    parser.add_argument("--token", help="Access Token for remote git")
    parser.add_argument("--non-interactive", help="Dont ask for input. Descriptions are blank unless you specifiy --description", action="store_true")
    parser.add_argument("--description", help="Description for a pull request")

    # template specific
    parser.add_argument("-p", "--problem", action="append", help="Problem")
    parser.add_argument("-f", "--fix", action="append", help="fix")
    parser.add_argument("-k", "--feature", action="append", help="feature")
    parser.add_argument("-n", "--note", action="append", help="notes")
    return parser.parse_args()


def get_remote_url(info: str) -> str:
    match = re.search(r"Push\s+URL: ([a-zA-Z0-9\.\-:@/_]+)", info, flags=re.IGNORECASE)

    if not match:
        raise LazyGitError("Remote url not found")
    return match.group(1)


def get_main_branch(info: str) -> str:
    match = re.search(r"HEAD\s+branch: ([a-zA-Z0-9\.\-:/]+)", info, flags=re.IGNORECASE)
    if not match:
        raise LazyGitError("Main remote branch not found")
    return match.group(1)



def main() -> None:
    args = parse_args()
    info = get_branch_info()
    title = args.title or get_last_commit_message()
    if args.block:
        title = f'Draft: {title}'
    target = args.target or get_main_branch(info)
    remote_url = args.repo or get_remote_url(info)
    source = args.source or get_remote_source_branch()
    token = args.token or TOKEN
    if not token:
        raise LazyGitError("No Credentials Found")
    handler = get_pr_handler(remote_url, token)
    if args.non_interactive:
        description = args.description or ''
    else:
        description = args.description or handler.get_description()
    push_source_branch()
    url = handler.open_pr(
        remote_url=remote_url,
        source=source,
        target=target,
        title=title,
        description=description or None,
        options={"block": args.block},
    )
    print(url)


if __name__ == "__main__":
    main()
