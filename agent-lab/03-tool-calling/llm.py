import os
import sys
from openai.types.chat import (
    ChatCompletionMessage,
    ChatCompletionMessageParam,
)

# Allow importing from the shared common package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common import DEFAULT_MODEL, get_client, loading

client = get_client()

# Named personas — swap via CLI: python main.py [model] [persona]
PERSONAS = {
    "default": (
        "You are a helpful assistant with access to real-time tools. "
        "Use the provided tools whenever you need current time or weather data to answer user queries."
    ),
    "engineer": (
        "You are a terse senior software engineer. "
        "Answer every question in two sentences maximum. "
        "No fluff, no pleasantries — just the answer. "
        "Use tools when needed, but keep output minimal."
    ),
    "tutor": (
        "You are a Socratic tutor. "
        "Never give direct answers or hand over code. "
        "Respond only with clarifying questions that guide the user to discover the solution themselves. "
        "If a tool result is available, ask the user what they think it means."
    ),
}


def create_initial_messages(persona: str = "default") -> list[ChatCompletionMessageParam]:
    """Return the initial conversation history with the selected persona as system prompt."""
    prompt = PERSONAS.get(persona, PERSONAS["default"])
    return [{"role": "system", "content": prompt}]


def call_llm(
    messages: list[ChatCompletionMessageParam] | list[object],
    tools: list[dict] | None = None,
    model: str = DEFAULT_MODEL,
) -> tuple[ChatCompletionMessage, object]:
    """Send conversation messages to the LLM and return (message, usage)."""
    kwargs: dict = {"model": model, "messages": messages}
    if tools:
        kwargs["tools"] = tools

    with loading("Thinking"):
        response = client.chat.completions.create(**kwargs)

    return response.choices[0].message, response.usage
