from typing import List, Protocol

from uaissistant.assistant.models import AssistantMessageItem
from uaissistant.assistant.schemas import AssistantEntity, AssistantThreadEntity


class LLM(Protocol):
    @property
    def source(self):
        pass

    async def create_assistant(
        self, name: str, instructions: str, model: str
    ) -> AssistantEntity:
        pass

    async def update_assistant(
        self,
        assistant_id,
        name,
        instructions,
        model,
    ) -> AssistantEntity:
        pass

    async def delete_assistant(self, assistant_id):
        pass

    async def create_thread(
        self, assistant_id: str, default_name: str
    ) -> AssistantThreadEntity:
        pass

    async def delete_thread(self, thread_id: str):
        pass

    async def process_user_message(
        self,
        assistant_id: str,
        thread_id: str,
        message: str,
    ) -> List[AssistantMessageItem]:
        pass

    async def update_tools(self, assistant_id):
        pass
