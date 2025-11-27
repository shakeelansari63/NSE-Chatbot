from typing import TypedDict


class GradioMessageContent(TypedDict):
    type: str
    text: str


class GradioMessage(TypedDict):
    role: str
    content: list[GradioMessageContent]
