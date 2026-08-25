# Week 03 AI Log

## Tool used
Antigravity IDE with Claude 3.5 Sonnet / Claude 3.7 Sonnet.

## Prompt given
I asked the AI to help me build tool-calling capabilities in Python, including safe tools like dice rolling and time checking, along with file reading, writing, and bash command execution. I also asked it to add user confirmation prompts for dangerous operations, handle git branching/PRs, and write a test script.

## What AI produced
It generated the Python functions for each tool, wrote the OpenAI-compatible JSON schemas, set up a tool registry, built the interactive confirmation prompt in the main loop, created the git feature branch, and wrote an automated test script.

## What I changed manually
I activated my virtual environment, exported my OpenRouter API key, authorized the GitHub device login in my browser, and merged the pull request into the main branch on GitHub.Also, I needed to make sure there are no bugs in the working model and tried testing it myself.

## How I verified it
I ran the test script in my terminal to make sure all tool functions passed, and then manually tested the chatbot loop by giving it prompts like checking the weather, rolling dice, reading files, and attempting file deletions to verify the yes/no confirmation prompt worked.

## What I still do not understand
How to safely prevent command injection in tools that run shell commands, so an LLM can't be tricked into executing harmful commands like rm -rf or chaining extra commands.
