#!/bin/bash
if [[ -z $1 ]]; then
    echo "Missing jira code"
    exit 1;
fi;
source /home/r/workspace/lazygit/ENV
CODE=$1
DEFAULT_BRANCH=$(git remote show origin | grep "HEAD branch" | sed 's/.*: //')
REPO_NAME=$(git remote -v | grep '(push)' | cut -d ":" -f 2 | cut -d "." -f 1)
SOURCE_BRNACH=$(git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/\1/')
TITLE=$(git log -1 --pretty=%s)
python /home/r/workspace/lazygit/lazy_push_handler.py "$REPO_NAME" --code "$CODE" --source "$SOURCE_BRNACH" --target "$DEFAULT_BRANCH" --message "$TITLE"
