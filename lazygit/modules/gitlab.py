from typing import List
import requests
from lazygit.modules.abstract import LazyGit

GITLAB_URL = "https://gitlab.com"

class LazyGitlab(LazyGit):

    @staticmethod
    def get_endpoint(endpoint: str, token: str) -> str:
        return f"{GITLAB_URL}/api/v4/{endpoint}?private_token={token}"

    @staticmethod
    def post_data(endpoint: str, token: str, data: dict):
        return requests.post(LazyGitlab.get_endpoint(endpoint, token), data=data)

    def open_pr(self, *, repo: str, source: str, target: str, title: str, description: str, labels: List[str]) -> int:
        labels = []
        response = self.post_data(
            "projects/%s/merge_requests" % repo,
            self.token,
            data={
                "source_branch": source,
                "target_branch": target,
                "title": title,
                "labels": ",".join(labels),
                "description": description,
                "remove_source_branch": True,
                "squash": True,
            },
        )
        return response.json()
