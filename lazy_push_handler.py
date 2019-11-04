from typing import Optional, Dict, Any
import argparse
import os
from pprint import pprint
from urllib import parse
import requests

TOKEN = os.environ.get('GITLAB_TOKEN')

URL = 'https://gitlab.com'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('repo', help="repo")
    parser.add_argument('-c', '--code', required=True, help="jira code")
    parser.add_argument('-s', '--source', required=True, help="source branch")
    parser.add_argument('-t', '--target', required=True, help="target branch")
    parser.add_argument('-m', '--message', required=True, help="Title of the pr")
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
            'labels': 'Release',
            'description': description,
        })
    return response


def main():
    args = parse_args()
    desc = 'Closes %s' % args.code.upper()
    pprint(open_pr(args.repo, args.source, args.target, args.message, desc))

if __name__ == '__main__':
    main()