from abc import ABC, abstractmethod
from typing import Optional
import os
import click


class LazyGit(ABC):
    def __init__(self, domain: str, path: str, token: str):
        self.path = path
        self.domain = domain
        self.token = token

    @property
    @abstractmethod
    def pr_template_file(self):
        pass

    def get_description(self) -> str:
        template = None
        if os.path.isfile(self.pr_template_file):
            with open(self.pr_template_file, encoding="utf-8") as fobj:
                template = fobj.read()
        description = click.edit(template)
        assert isinstance(description, str)
        return description

    @abstractmethod
    def open_pr(
        self,
        *,
        remote_url: str,
        source: str,
        target: str,
        title: str,
        description: Optional[str],
        options: Optional[dict] = None
    ) -> str:
        raise NotImplementedError
