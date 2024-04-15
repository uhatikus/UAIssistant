import re
import uuid
from datetime import datetime
from typing import List

from anthropic import Anthropic
from anthropic.resources.beta.tools.messages import ToolsBetaMessage
from uaissistant.assistant.models import (
    AssistantMessageItem,
    AssistantMessageValue,
)
from uaissistant.assistant.schemas import (
    AssistantEntity,
    AssistantMessageEntity,
    AssistantMessageType,
    AssistantThreadEntity,
    LLMSource,
    Role,
)
from uaissistant.llms.anthropic.repository import IAnthropicRepository
from uaissistant.llms.llm import LLM
from uaissistant.tool_factory import tools
from uaissistant.tool_factory.service import IToolFactoryService
from uaissistant.tool_factory.schemas.tool_function import ToolFunction


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

        self.temperature = 0.1
        self.API_TIMEOUT = 10

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
        self._self_update_tools()
        assistant = AssistantEntity(
            id=assistant_id,
            name=name,
            created_at=datetime.now(),
            instructions=instructions,
            model=model,
            llmsource=self.source,
        )
        return assistant

    async def delete_assistant(self, assistant_id: str):
        return

    async def create_thread(
        self, assistant_id: str, default_name: str
    ) -> AssistantThreadEntity:
        thread = AssistantThreadEntity(
            id=f"claude_thread_{str(uuid.uuid4())}",
            name=default_name,
            assistant_id=assistant_id,
            created_at=datetime.now(),
        )
        return thread

    async def delete_thread(self, thread_id: str):
        return

    async def process_user_message(
        self,
        assistant: AssistantEntity,
        thread_id: str,
        message: str,
    ) -> List[AssistantMessageItem]:
        print(
            f"[{self.__class__.__name__}: process_user_message] you message '{message}' is being sent to the assistant"
        )
        # define user message
        user_message = AssistantMessageItem(
            id=f"user2claude_message_{str(uuid.uuid4())}",
            role=Role.User,
            created_at=datetime.now(),
            value=AssistantMessageValue(
                type=AssistantMessageType.Text, content={"message": message}
            ),
        )

        # prepare messages for Anthropic
        old_messages: List[
            AssistantMessageEntity
        ] = await self.anthropic_repository.list_old_messages(
            thread_id=thread_id
        )
        messages_for_anthropic = [
            {"role": m.role, "content": m.content["message"]}
            for m in old_messages
            if "message" in m.content
        ]

        # add new user message
        user_message_for_anthropic = {
            "role": "user",
            "content": message,
        }
        messages_for_anthropic.append(user_message_for_anthropic)

        # output list
        frontend_outputs: List[AssistantMessageItem] = []

        # initial anthropic call
        response: ToolsBetaMessage = self.client.beta.tools.messages.create(
            model=assistant.model,
            max_tokens=1024,
            tools=self.anthropic_tools,
            system=assistant.instructions,
            messages=messages_for_anthropic,
            temperature=self.temperature,
            timeout=self.API_TIMEOUT,
        )

        messages_for_anthropic.append(
            {"role": response.role, "content": response.content}
        )
        tool_outputs = []

        while response.stop_reason == "tool_use":
            print(
                f"[{self.__class__.__name__}: process_user_message] current response {response.content}"
            )
            for content in response.content:
                # skip text and other non-tool-function content
                if content.type != "tool_use":
                    continue

                print(
                    f"[{self.__class__.__name__}: process_user_message] executing function {content.name}, with args: {content.input}"
                )

                # call tool_function
                (
                    output,
                    new_frontend_contents,
                ) = self.tool_factory.call_tool_function(
                    function_name=content.name, args=content.input
                )

                # save the resulted ouputs
                tool_outputs.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": content.id,  # from the API response
                        "content": output,  # from running your tool
                    }
                )
                frontend_outputs.extend(new_frontend_contents)

            # submit the results of the tool-functions
            messages_for_anthropic.append(
                {"role": "user", "content": tool_outputs}
            )
            response: ToolsBetaMessage = self.client.beta.tools.messages.create(
                model=assistant.model,
                max_tokens=1024,
                tools=self.anthropic_tools,
                system=assistant.instructions,
                messages=messages_for_anthropic,
                temperature=self.temperature,
                timeout=self.API_TIMEOUT,
            )
            messages_for_anthropic.append(
                {"role": response.role, "content": response.content}
            )
            tool_outputs = []

        # prepare the final message from the LLM
        # for each message, create a value wrapper.
        for content in response.content:
            if content.text is not None:
                initial_claude_response = content.text
                print(
                    f"[{self.__class__.__name__}: process_user_message] initial claude response: {initial_claude_response}"
                )
                content_message = self._remove_thinking_tags(
                    initial_claude_response
                )
                assistant_frontent_output = AssistantMessageItem(
                    id=f"claude_message_{str(uuid.uuid4())}",
                    role=Role.Assistant,
                    created_at=datetime.now(),
                    value=AssistantMessageValue(
                        type=AssistantMessageType.Text,
                        content={"message": content_message},
                    ),
                )
                frontend_outputs.append(assistant_frontent_output)

        responses = frontend_outputs

        user_message_and_responses = [user_message] + responses
        return user_message_and_responses

    async def update_tools(self, assistant_id: str):
        self._self_update_tools()

    def _self_update_tools(self):
        # gather tools information
        self.anthropic_tools = []
        for function_name in [
            attr for attr in dir(tools) if callable(getattr(tools, attr))
        ]:
            function: ToolFunction = getattr(tools, function_name)
            self.anthropic_tools.append(function.anthropicschema)

    def _remove_thinking_tags(self, text):
        # Define the pattern to match <thinking> ... </thinking> tags
        pattern = re.compile(r"<thinking>.*?</thinking>\n\n", re.DOTALL)

        # Remove everything inside <thinking> tags
        cleaned_text = re.sub(pattern, "", text)

        return cleaned_text
