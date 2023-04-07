from abc import ABC, abstractmethod
from typing import List


class LazyGit(ABC):
    def __init__(self, token: str):
        self.token = token

    @abstractmethod
    def open_pr(self, *, repo: str, source: str, target: str, title: str, description: str, labels: List[str]) -> int:
        raise NotImplementedError
