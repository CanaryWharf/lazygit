from typing import Optional
from urllib import parse
import requests
from lazygit.modules.abstract import LazyGit


class GitlabHandler(LazyGit):
    pr_template_file = ".gitlab/merge_request_templates/default.md"

    def get_endpoint(self, endpoint: str, token: str) -> str:
        return f"{self.domain}/api/v4/{endpoint}?private_token={token}"

    def post_data(self, endpoint: str, token: str, data: dict):
        return requests.post(self.get_endpoint(endpoint, token), data=data, timeout=30)

    @staticmethod
    def get_repo_id(repo: str) -> str:
        return parse.quote_plus(repo)

    def open_pr(
        self,
        *,
        remote_url: str,
        source: str,
        target: str,
        title: str,
        description: Optional[str],
        options: Optional[dict] = None,
    ) -> str:
        labels = []
        block = (options or {}).get("block", False)
        if block:
            labels.append("Blocked")
        else:
            labels.append("In Review")
        response = self.post_data(
            f"projects/{self.get_repo_id(self.path)}/merge_requests",
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
        if response.status_code >= 400:
            print(response.json())
        response.raise_for_status()
        return response.json()["web_url"]
