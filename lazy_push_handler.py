# pylint: disable=too-many-arguments
from typing import Optional, Dict, Any
import argparse
import os
from pprint import pprint
from urllib import parse
import shlex
import subprocess
import requests
import pyperclip

TOKEN = os.environ.get('GITLAB_TOKEN')

URL = 'https://gitlab.com'

PROBLEM_TEMPLATE = '''
## Problems:
{problems}
'''


FIX_TEMPLATE = '''
## Fixes:
{fixes}
'''

NOTE_TEMPLATE = '''
## Notes
{notes}
'''

FEATURE_TEMPLATE = '''
## Feature:
{features}
'''

def run(cmd):
    return subprocess.check_output(shlex.split(cmd))

def notify(msg):
    run(f'notify-send -i info "{msg}"')

def get_default_branch():
    origins = run('git remote show origin').decode().strip()
    origin = [x for x in origins.split('\n') if 'HEAD branch' in x][0].split(':')[-1].strip()
    return origin


def get_repo_name():
    push_repos = run('git remote -v').decode().strip()
    push_repo = [x for x in push_repos.split('\n') if '(push)' in x][0].split(':')[-1].split('.')[0]
    return push_repo

def get_source_branch():
    return run('git symbolic-ref --short HEAD').decode().strip()

def get_pr_title():
    return run('git log -1 --pretty=%s').decode().strip()


def push_source_branch(branch):
    run(f'git push -u origin "{branch}"')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--repo', help="repo url")
    parser.add_argument('-c', '--code', help="jira code")
    parser.add_argument('-s', '--source', help="source branch")
    parser.add_argument('-t', '--target', help="target branch")
    parser.add_argument('-m', '--message', help="Title of the pr")
    parser.add_argument('-p', '--problem', action='append', help="Problem")
    parser.add_argument('-f', '--fix', action='append', help="fix")
    parser.add_argument('-k', '--feature', action='append', help="feature")
    parser.add_argument('-n', '--note', action='append', help="notes")
    parser.add_argument('-b', '--block', action='store_true', help="notes")
    return parser.parse_args()


def get_endpoint(endpoint: str, token: str, params: Optional[Dict[str, str]] = None) -> str:
    parsed_params = ''
    if params:
        parsed_params = parse.urlencode(params)
    return '%s/api/v4/%s?private_token=%s&%s' % (URL, endpoint, token, parsed_params)


def post_data(endpoint: str, token: str, data: Dict[str, Any]):
    response = requests.post(get_endpoint(endpoint, token), data=data)
    return response

def open_pr(repo, source, target, title, description, block=False):
    labels = []
    if block:
        labels.append('Blocked')
    else:
        labels.append('In Review')
    response = post_data(
        'projects/%s/merge_requests' % repo,
        TOKEN,
        data={
            'source_branch': source,
            'target_branch': target,
            'title': title,
            'labels': ','.join(labels),
            'description': description,
            'remove_source_branch': True,
            'squash': True,
        })
    return response.json()


def main():
    args = parse_args()
    desc = ''
    if args.feature:
        features = '\n'.join([f'  * {x}' for x in args.feature])
        desc += FEATURE_TEMPLATE.format(features=features)

    if args.problem:
        problems = '\n'.join([f'  * {x}' for x in  args.problem])
        desc += PROBLEM_TEMPLATE.format(problems=problems)

    if args.fix:
        fixes = '\n'.join([f'  * {x}' for x in  args.fix])
        desc += FIX_TEMPLATE.format(fixes=fixes)

    if args.note:
        notes = '\n'.join([f'  * {x}' for x in args.note])
        desc += NOTE_TEMPLATE.format(notes=notes)

    desc = desc or None
    title = args.message or get_pr_title()
    source = args.source or get_source_branch()
    target = args.target or get_default_branch()
    repo = args.repo or get_repo_name()
    push_source_branch(source)
    res = open_pr(parse.quote_plus(repo), source, target, title, desc, args.block)
    web_url = res.get('web_url')
    if web_url:
        pyperclip.copy(web_url)
        notify('URL copied')
    pprint(web_url or res)

if __name__ == '__main__':
    main()
