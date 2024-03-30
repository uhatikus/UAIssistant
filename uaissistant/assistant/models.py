from datetime import datetime
from typing import Any, List

from pydantic.dataclasses import dataclass

from uaissistant.assistant.schemas import (
    AssistantEntity,
    AssistantThreadEntity,
    LLMSource,
    Role,
    AssistantMessageType,
)


# For Messages
@dataclass
class AssistantMessageValue:
    type: AssistantMessageType
    content: dict[str, Any]


@dataclass
class AssistantMessageItem:
    id: str
    role: Role
    created_at: datetime
    value: AssistantMessageValue


# For GET requests
@dataclass
class ListAssistantsResult:
    assistants: List[AssistantEntity]


@dataclass
class ListThreadsResult:
    threads: List[AssistantThreadEntity]


@dataclass
class ListMessageResult:
    messages: List[AssistantMessageItem]


# For POST requests
@dataclass
class CreateAssistantParams:
    name: str
    instructions: str
    llmsource: LLMSource
    model: str


@dataclass
class CreateThreadParams:
    message: str


@dataclass
class CreateThreadResult(AssistantThreadEntity):
    messages: List[AssistantMessageItem]


@dataclass
class SendMessageParams:
    message: str


@dataclass
class SendMessageResult:
    thread_id: str
    messages: List[AssistantMessageItem]


# For PATCH requests
@dataclass
class UpdateAssistantParams:
    name: str
    instructions: str
    model: str


@dataclass
class UpdateThreadParams:
    name: str
