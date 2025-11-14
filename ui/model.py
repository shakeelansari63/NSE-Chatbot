from typing import TypedDict


class OpenAIMessage(TypedDict):
    content: str
    role: str


class Socials(TypedDict):
    github: str
