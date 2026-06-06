import os
import re
from datetime import datetime

from langchain_core.messages import (
    BaseMessage,
    get_buffer_string,
)

_MAX_USER_INPUT_LENGTH = 2000

_PROMPT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts")


def _load_prompt(name: str) -> str:
    path = os.path.join(_PROMPT_DIR, name)
    with open(path, encoding="utf-8") as f:
        return f.read()


def sanitize_user_text(text: str) -> str:
    """Strip control characters and limit length to prevent prompt injection."""
    # Remove null bytes and other control characters except newline/tab
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return cleaned.strip()[-_MAX_USER_INPUT_LENGTH:]


def get_execution_system_message() -> str:
    template = _load_prompt("execution_system.md")
    return template.replace(
        "{{CURRENT_DATE}}",
        datetime.now().strftime("%A, %d %B %Y"),
    )


def get_out_of_scope_system_message(user_conversation: list[BaseMessage]) -> str:
    template = _load_prompt("out_of_scope.md")
    return template.replace(
        "{{CONVERSATION}}",
        sanitize_user_text(get_buffer_string(user_conversation)),
    )


def get_shortlist_message(tools: list[str], user_conversation: list[BaseMessage]) -> str:
    template = _load_prompt("shortlist.md")
    template = template.replace("{{TOOLS}}", ", ".join(tools))
    return template.replace(
        "{{CONVERSATION}}",
        sanitize_user_text(get_buffer_string(user_conversation)),
    )
