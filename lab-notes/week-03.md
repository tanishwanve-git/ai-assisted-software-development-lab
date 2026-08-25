# Week 03 AI Log

## Tool used
Antigravity IDE with Claude 3.5 Sonnet / Claude 3.7 Sonnet.

## Prompt given
Asked the AI to implement new tools (`roll_dice`, `get_time_in`, `delete_file`, `read_file`, `write_file`, and `run_bash`) in `tools.py` with OpenAI function schemas, add confirmation message for dangerous operations in `main.py`, create a git feature branch, open a PR, and write a bash test suite.

## What AI produced
The AI wrote the tool functions, created the corresponding JSON schemas, updated the tool registry, added interactive `input()` confirmation prompts for destructive tools, managed git branching and PR creation, and created `test_tools.py`.

## What I changed manually
I ran the environment activation commands, set my `OPENROUTER_API_KEY`, approved terminal prompts, completed the GitHub web device login flow (`gh auth login`), and merged the pull request into `main` directly on GitHub.

## How I verified it
I executed `python3 test_tools.py` in the terminal to verify all 23 unit tests passed across all tools, and interactively tested `main.py` with real prompts (weather, dice rolls, file reads, and file deletions with `y/n` confirmation prompts).

## What I still do not understand
How to prevent run_bash from being abused with command injection—like if someone tricks the LLM into running rm -rf / or chaining extra commands with ; or &&.
