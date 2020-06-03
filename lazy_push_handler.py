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

TEMPLATE = '''
## Problem:
{problems}

## Fix:
{fixes}

'''

def notify(msg):
    subprocess.run(shlex.split(f'notify-send -i info "{msg}"')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('repo', help="repo")
    parser.add_argument('-c', '--code', help="jira code")
    parser.add_argument('-s', '--source', required=True, help="source branch")
    parser.add_argument('-t', '--target', required=True, help="target branch")
    parser.add_argument('-m', '--message', required=True, help="Title of the pr")
    parser.add_argument('-p', '--problem', action='append', help="Problem")
    parser.add_argument('-f', '--fix', action='append', help="fix")
    return parser.parse_args()


def get_endpoint(endpoint: str, token: str, params: Optional[Dict[str, str]] = None) -> str:
    parsed_params = ''
    if params:
        parsed_params = parse.urlencode(params)
    return '%s/api/v4/%s?per_page=100&private_token=%s&%s' % (URL, endpoint, token, parsed_params)


def post_data(endpoint: str, token: str, data: Dict[str, Any]):
    response = requests.post(get_endpoint(endpoint, token), data=data)
    return response

def open_pr(repo, source, target, title, description):
    response = post_data(
        'projects/%s/merge_requests' % repo,
        TOKEN,
        data={
            'source_branch': source,
            'target_branch': target,
            'title': title,
            'labels': 'In Review',
            'description': description,
            'remove_source_branch': True,
            'squash': True,
        })
    return response.json()


def main():
    args = parse_args()
    if args.problem and args.fix:
        problems = '\n'.join([f'  * {x}' for x in  args.problem])
        fixes = '\n'.join([f'  * {x}' for x in  args.fix])
        desc = TEMPLATE.format(problems=problems, fixes=fixes)
    else:
        desc = None
    title = args.message
    res = open_pr(parse.quote_plus(args.repo), args.source, args.target, title, desc)
    print('-' * 10)
    web_url = res.get('web_url')
    if web_url:
        pyperclip.copy(web_url)
        notify('URL copied')
    pprint(web_url or res)

if __name__ == '__main__':
    main()
