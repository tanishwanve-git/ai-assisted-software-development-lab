import json
import os
import sys
from openai.types.chat import ChatCompletionMessageParam

# Allow importing from the shared common package and local directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from common import DEFAULT_MODEL

from llm import call_llm, create_initial_messages
from tools import AVAILABLE_TOOLS, DANGEROUS_TOOLS, TOOLS_SCHEMA

# ── CLI args ────────────────────────────────────────────────
# Usage: python main.py [model] [persona]
# Personas: default | engineer | tutor
model   = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL
persona = sys.argv[2] if len(sys.argv) > 2 else "default"

# ── Rung 3: Context budget ──────────────────────────────────
TOKEN_BUDGET = 4000  # drop old turns when session crosses this

def trim_messages(msgs: list) -> list:
    """Drop oldest non-system user/assistant pairs to stay within budget."""
    while len(msgs) > 3:
        # Rough estimate: ~4 chars per token
        est = sum(len(str(m.get("content", ""))) // 4 for m in msgs)
        if est <= TOKEN_BUDGET // 2:
            break
        # Remove oldest user turn (index 1) + its assistant reply (index 2)
        msgs.pop(1)
        if len(msgs) > 1:
            msgs.pop(1)
    return msgs

# ── Session state ───────────────────────────────────────────
messages: list[ChatCompletionMessageParam] = create_initial_messages(persona=persona)
total_in  = 0
total_out = 0

print(f"\n--- Chat with Tools Started ---")
print(f"Model  : {model}")
print(f"Persona: {persona}")
print(f"Budget : {TOKEN_BUDGET} tokens")
print("Available tools: get_current_time, get_current_weather, roll_dice,")
print("                 get_time_in, delete_file, read_file, write_file, run_bash")
print("Type 'exit' or 'quit' to stop.\n")


def _run_tool(function_name: str, arguments: dict) -> str:
    """Dispatch a tool call, prompting confirmation for dangerous tools."""
    print(f"\n⚙️  Tool Call: {function_name}({arguments})")
    if function_name in DANGEROUS_TOOLS:
        confirm = input(f"⚠️  '{function_name}' is a dangerous operation. Proceed? (y/n): ")
        if confirm.strip().lower() != "y":
            print("🚫 Tool execution denied by user.\n")
            return f"Tool '{function_name}' was denied by the user."
    tool_fn = AVAILABLE_TOOLS.get(function_name)
    result  = tool_fn(**arguments) if tool_fn else f"Error: Tool '{function_name}' not found"
    print(f"📥 Tool Output: {result}\n")
    return result


def _show_usage(usage) -> None:
    """Rung 2: print per-turn and running session token counts."""
    global total_in, total_out
    if not usage:
        return
    total_in  += usage.prompt_tokens
    total_out += usage.completion_tokens
    session    = total_in + total_out
    print(f"📊 Tokens — in: {usage.prompt_tokens:,} | out: {usage.completion_tokens:,} | session: {session:,}")


# ── Interactive chat loop ───────────────────────────────────
while True:
    user_message = input("User: ")
    if user_message.strip().lower() in ["exit", "quit"]:
        print(f"\nExiting chat. Session total: {total_in + total_out:,} tokens. Bye!")
        break

    # Rung 3: trim if over budget before adding new turn
    if total_in + total_out >= TOKEN_BUDGET:
        print(f"⚠️  Budget crossed ({TOKEN_BUDGET} tokens). Trimming old turns...\n")
        messages = trim_messages(messages)

    # 1. Append user input to history
    messages.append({"role": "user", "content": user_message})

    # 2. Call LLM — now returns (message, usage)
    response_message, usage = call_llm(messages, tools=TOOLS_SCHEMA, model=model)
    _show_usage(usage)

    # 3. Tool execution loop (supports chained multi-tool calls)
    while response_message.tool_calls:
        # Append assistant's tool call request to history
        messages.append(
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in response_message.tool_calls
                    if tc.type == "function"
                ],
            }
        )

        for tool_call in response_message.tool_calls:
            if tool_call.type != "function":
                continue
            function_name = tool_call.function.name
            arguments     = json.loads(tool_call.function.arguments)
            result        = _run_tool(function_name, arguments)

            # Append tool result to conversation history
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                }
            )

        # Let the model process tool output and produce a reply (or call more tools)
        response_message, usage = call_llm(messages, tools=TOOLS_SCHEMA, model=model)
        _show_usage(usage)

    assistant_reply = response_message.content or ""
    print(f"\nModel: {assistant_reply}\n")

    # 4. Append assistant's final text reply to history
    messages.append({"role": "assistant", "content": assistant_reply})

