from typing import Tuple
import re
from lazygit.exceptions import LazyGitError
from lazygit.modules.abstract import LazyGit
from lazygit.modules.gitlab import LazyGitlabHandler

DOMAIN_MAPPINGS = {
    "https://gitlab.com": LazyGitlabHandler,
}

def get_domain_and_path(remote_url: str) -> Tuple[str, str]:
    regex = (
        r"((git@)|(https:\/\/))(([a-zA-Z0-9]+):([a-zA-Z0-9]+)@)?"
        r"(?P<domain>[a-z0-9.]+)(\/|:)(?P<repo_path>[_\-\.a-zA-Z0-9\/]+).git"
    )
    match = re.match(regex, remote_url)
    if not match:
        raise LazyGitError("Could not find domain")
    domain = match.group("domain")
    path = match.group("repo_path")
    if not domain or not path:
        raise LazyGitError("Could not find domain")
    return f'https://{domain}', path


def get_pr_handler(remote_url: str, token: str) -> LazyGit:
    domain, path = get_domain_and_path(remote_url)
    if domain not in DOMAIN_MAPPINGS:
        raise LazyGitError("Domain not recognised")
    return DOMAIN_MAPPINGS[domain](domain, path, token)
