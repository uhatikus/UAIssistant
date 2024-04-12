import uuid
import textwrap
from datetime import datetime
from typing import List
from environs import Env
import google.generativeai as genai
import google.ai.generativelanguage as glm
from google.generativeai.types import GenerateContentResponse

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
from uaissistant.llms.gemini.repository import IGeminiRepository
from uaissistant.llms.llm import LLM
from uaissistant.tool_factory import tools
from uaissistant.tool_factory.service import IToolFactoryService
from uaissistant.tool_factory.schemas.tool_function import ToolFunction

from IPython.display import Markdown


class GeminiLLM(LLM):
    def __init__(
        self,
        env: Env,
        tool_factory: IToolFactoryService,
        gemini_repository: IGeminiRepository,
    ):
        genai.configure(api_key=env.str("GEMINI_API_KEY"))
        self.tool_factory = tool_factory
        self.gemini_repository = gemini_repository

        self._self_update_tools()

    @property
    def source(self):
        return LLMSource.Gemini

    async def create_assistant(
        self, name: str, instructions: str, model: str
    ) -> AssistantEntity:
        assistant = AssistantEntity(
            id=f"gemini_asst_{str(uuid.uuid4())}",
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
            id=f"gemini_thread_{str(uuid.uuid4())}",
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
            id=f"user2gemini_message_{str(uuid.uuid4())}",
            role=Role.User,
            created_at=datetime.now(),
            value=AssistantMessageValue(
                type=AssistantMessageType.Text, content={"message": message}
            ),
        )

        # prepare messages for Gemini
        old_messages: List[
            AssistantMessageEntity
        ] = await self.gemini_repository.list_old_messages(thread_id=thread_id)
        messages_for_gemini = [
            {
                "role": "model" if m.role == "assistant" else m.role,
                "parts": [m.content["message"]],
            }
            for m in old_messages
            if "message" in m.content
        ]

        # add new user message
        user_message_for_gemini = {
            "role": "user",
            "parts": [message],
        }
        messages_for_gemini.append(user_message_for_gemini)

        # output list
        frontend_outputs: List[AssistantMessageItem] = []

        # use gemini model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro-latest",  # assistant.model,
            tools=glm.Tool(function_declarations=self.gemini_tools),
            system_instruction=assistant.instructions,
        )

        # initial gemini call
        response: GenerateContentResponse = model.generate_content(
            messages_for_gemini
        )
        # role = response._result.candidates[0].content.role
        parts = response._result.candidates[0].content.parts
        messages_for_gemini.append(
            {
                "role": "model",
                "parts": parts,
            }
        )
        tool_outputs = []

        while any("function_call" in part for part in parts):
            print(
                f"[{self.__class__.__name__}: process_user_message] current response {parts}"
            )
            for part in parts:
                # skip text and other non-tool-function content
                if "function_call" not in part:
                    continue

                print(
                    f"[{self.__class__.__name__}: process_user_message] executing function {part.function_call.name}, with args: {dict(part.function_call.args)}"
                )

                # call tool_function
                (
                    output,
                    new_frontend_contents,
                ) = self.tool_factory.call_tool_function(
                    function_name=part.function_call.name,
                    args=part.function_call.args,
                )

                # save the resulted ouputs
                tool_outputs.append(
                    glm.Part(
                        function_response=glm.FunctionResponse(
                            name=part.function_call.name,
                            response={"result": output},
                        )
                    )
                )
                frontend_outputs.extend(new_frontend_contents)

            # submit the results of the tool-functions
            messages_for_gemini.append({"role": "user", "parts": tool_outputs})
            response: GenerateContentResponse = model.generate_content(
                messages_for_gemini
            )
            parts = response._result.candidates[0].content.parts
            print("parts")
            print(parts)
            print("messages_for_gemini")
            print(messages_for_gemini)
            new_parts = []
            if any("function_call" in part for part in parts):
                for part in parts:
                    if "text" not in part:
                        new_parts.append(part)
            else:
                break
            print("new_parts")
            print(new_parts)
            messages_for_gemini.append({"role": "model", "parts": new_parts})
            tool_outputs = []

        # prepare the final message from the OpenAI Assistant
        # for each message, create a value wrapper.
        for part in parts:
            if "text" in part:
                print(
                    f"[{self.__class__.__name__}: process_user_message] response: {part.text}"
                )
                assistant_frontent_output = AssistantMessageItem(
                    id=f"gemini_message_{str(uuid.uuid4())}",
                    role=Role.Assistant,
                    created_at=datetime.now(),
                    value=AssistantMessageValue(
                        type=AssistantMessageType.Text,
                        content={"message": part.text},
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
        self.gemini_tools = []
        for function_name in [
            attr for attr in dir(tools) if callable(getattr(tools, attr))
        ]:
            function: ToolFunction = getattr(tools, function_name)
            self.gemini_tools.append(function.geminischema)

    def _to_markdown(self, text):
        text = text.replace("•", "  *")
        return Markdown(textwrap.indent(text, "> ", predicate=lambda _: True))
