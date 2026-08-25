Week 04 AI Log — Tool Calling & Agent Capabilities

What I built or worked on today: 
Today I built and expanded an interactive CLI agent with tool-calling capabilities in Python (03-tool-calling). 
I implemented new tools for performing math (calculator) alongside existing weather, time, dice rolling, and file deletion tools.

Tool used: 
Antigravity AI (Gemini 3.6 Flash) & VS Code / Terminal (python3 main.py).

How I used AI today: tutor (explain) or typist (write)? — one concrete example: I used AI as a tutor to explain why redundant type casts like int(sides) and str(result) triggered linter warnings, as well as why Pyrefly threw virtual file parse errors when inspecting isolated code blocks.

What I wrote / figured out myself: I wired up read_file, write_file, run_bash, and calculator into AVAILABLE_TOOLS, registered their parameters in TOOLS_SCHEMA, and verified that destructive operations (write_file, run_bash, delete_file) trigger safety confirmation prompts before running.

How I verified it works: I ran python3 main.py in the terminal and executed both individual commands (rolling dice, checking python version with bash, calculating expressions) and a multi-tool chain where the LLM fetched London weather, wrote it to weather.txt, and read the file back in one conversation turn.

What I still don't understand: I want to explore more about how the model decides when to chain multiple tool calls autonomously in a single turn versus waiting for user feedback between calls.
