from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class LLMSource(Enum):
    OpenAI = "openai"
    Anthropic = "anthropic"
    Gemini = "gemini"


@dataclass
class AssistantEntity:
    id: str
    name: str
    created_at: datetime
    instructions: str
    model: str
    llmsource: LLMSource


@dataclass
class AssistantThreadEntity:
    id: str
    name: str
    assistant_id: str
    created_at: datetime


class Role(Enum):
    Assistant = "assistant"
    User = "user"


class AssistantMessageType(Enum):
    Text = "text"
    Plot = "plotly_json"
    File = "file"


@dataclass
class AssistantMessageEntity:
    id: str
    assistant_id: str
    thread_id: str
    created_at: datetime
    role: Role
    type: AssistantMessageType
    content: dict[str, Any]
