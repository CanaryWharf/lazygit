# Lazy Git
For when you want to make PRs without visiting the website

## Installation
- Clone the repo
- run a `pip install lazygit/`

NOTE: If you want to use a specific editor (Not the terminal default, usually vi), you'll need to set the `$EDITOR` env var
For vscode, you should add the following to your env vars
```
export EDITOR="code --wait"
```

## Usage
After ccommitting your work, you can run
```
git pr
```
Which will open up the your editor, allowing you to make changes.
If you have a standard PR template, lazygit will open that allowing you to make changes.
NOTE: you will need to save **AND** close** the file for lazygit to work

### Using in scripts
You can also use this in scripts with the `--non-interactive` and `--description` flags. Which will tell lazygit to not open a text editor, and to take the description/body from the command line instead
