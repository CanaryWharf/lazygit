from typing import Optional
from urllib import parse
import requests
from lazygit.modules.abstract import LazyGit


class GithubHandler(LazyGit):
    pr_template_file = ".github/pull_request_template.md"
    api_domain = "https://api.github.com"

    def post_data(self, endpoint: str, token: str, data: dict):
        return requests.post(f"{self.api_domain}/{endpoint}", json=data, headers={"Authorization": f"Bearer {token}"}, timeout=30)

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
        block = (options or {}).get("block", False)
        response = self.post_data(
            f"repos/{self.path}/pulls",
            self.token,
            data={
                "head": source,
                "base": target,
                "title": title,
                "body": description,
                "draft": block,
            },
        )
        if response.status_code >= 400:
            print(response.json())
        response.raise_for_status()
        return response.json()["html_url"]
