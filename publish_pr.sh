#!/bin/bash

function handle_error() {
    notify-send -i info "Something went wrong"
}
source /home/r/workspace/lazygit/ENV
source /home/r/workspace/lazygit/venv/bin/activate
python /home/r/workspace/lazygit/lazy_push_handler.py "$@"
