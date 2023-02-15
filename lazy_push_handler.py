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

def notify(msg):
    subprocess.run(shlex.split(f'notify-send -i info "{msg}"'), check=False)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('repo', help="repo")
    parser.add_argument('-c', '--code', help="jira code")
    parser.add_argument('-s', '--source', required=True, help="source branch")
    parser.add_argument('-t', '--target', required=True, help="target branch")
    parser.add_argument('-m', '--message', required=True, help="Title of the pr")
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
    return '%s/api/v4/%s?per_page=100&private_token=%s&%s' % (URL, endpoint, token, parsed_params)


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
    title = args.message
    res = open_pr(parse.quote_plus(args.repo), args.source, args.target, title, desc, args.block)
    print('-' * 10)
    web_url = res.get('web_url')
    if web_url:
        pyperclip.copy(web_url)
        notify('URL copied')
    pprint(web_url or res)

if __name__ == '__main__':
    main()
