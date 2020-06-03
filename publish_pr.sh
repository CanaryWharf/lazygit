#!/bin/bash
source /home/r/workspace/lazygit/ENV
source /home/r/workspace/lazygit/venv/bin/activate
DEFAULT_BRANCH=$(git remote show origin | grep "HEAD branch" | sed 's/.*: //')
REPO_NAME=$(git remote -v | grep '(push)' | cut -d ":" -f 2 | cut -d "." -f 1)
SOURCE_BRANCH=$(git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/\1/')
TITLE=$(git log -1 --pretty=%s)
git push -u origin "$SOURCE_BRANCH"
python /home/r/workspace/lazygit/lazy_push_handler.py "$REPO_NAME" --source "$SOURCE_BRANCH" --target "$DEFAULT_BRANCH" --message "$TITLE" "$@"
