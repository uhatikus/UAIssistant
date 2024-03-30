import uuid
from datetime import datetime
from typing import List, Tuple

from anthropic import Anthropic
from uaissistant.assistant.models import AssistantMessageItem
from uaissistant.assistant.schemas import (
    AssistantEntity,
    AssistantThreadEntity,
    LLMSource,
)
from uaissistant.llms.anthropic.repository import IAnthropicRepository
from uaissistant.llms.llm import LLM
from uaissistant.tool_factory import tools
from uaissistant.tool_factory.service import IToolFactoryService
from uaissistant.tool_factory.tools.schema import ToolFunction


class AnthropicLLM(LLM):
    def __init__(
        self,
        client: Anthropic,
        tool_factory: IToolFactoryService,
        anthropic_repository: IAnthropicRepository,
    ):
        self.client = client
        self.tool_factory = tool_factory
        self.anthropic_repository = anthropic_repository

        self._self_update_tools()

    @property
    def source(self):
        return LLMSource.Anthropic

    async def create_assistant(
        self, name: str, instructions: str, model: str
    ) -> AssistantEntity:
        assistant = AssistantEntity(
            id=f"claude_asst_{str(uuid.uuid4())}",
            name=name,
            created_at=datetime.now(),
            instructions=instructions,
            model=model,
            llmsource=self.source,
        )
        return assistant

    async def update_assistant(
        self,
        assistant_id,
        name,
        instructions,
        model,
    ) -> AssistantEntity:
        # self._self_update_tools()
        assistant = AssistantEntity(
            id=assistant_id,
            name=name,
            created_at=datetime.now(),
            instructions=instructions,
            model=model,
            llmsource=self.source,
        )
        return assistant

    async def delete_assistant(self, assistant_id):
        return

    async def create_thread(self, default_name) -> AssistantThreadEntity:
        thread = AssistantThreadEntity(
            id=f"claude_asst_{str(uuid.uuid4())}",
            name=default_name,
            created_at=datetime.now(),
        )
        return thread

    async def delete_thread(self, thread_id):
        return

    async def process_user_message(
        self,
        assistant_id: str,
        thread_id: str,
        message: str,
    ) -> Tuple[AssistantMessageItem, List[AssistantMessageItem]]:
        # TODO: improve
        message = self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[{"role": "user", "content": "Hello, Claude"}],
        )
        print(message.content)

    async def update_tools(self, assistant_id):
        # TODO: improve
        pass

    def _self_update_tools(self):
        # gather tools information
        # TODO: use XML
        self.openai_tools = [{"type": "code_interpreter"}]
        for function_name in [
            attr for attr in dir(tools) if callable(getattr(tools, attr))
        ]:
            function: ToolFunction = getattr(tools, function_name)
            tool_function_defenition = {
                "type": "function",
                "function": function.openaischema,
            }
            self.openai_tools.append(tool_function_defenition)
