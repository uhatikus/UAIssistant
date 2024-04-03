import json
import time
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Tuple

from uaissistant.assistant.models import (
    AssistantMessageItem,
    AssistantMessageValue,
)
from uaissistant.assistant.schemas import (
    AssistantEntity,
    AssistantThreadEntity,
    LLMSource,
    Role,
    AssistantMessageType,
)
from uaissistant.llms.llm import LLM
from uaissistant.tool_factory import tools
from uaissistant.tool_factory.service import IToolFactoryService
from uaissistant.tool_factory.schemas.tool_function import ToolFunction
from openai import Client
from openai.types.beta.threads import Run


class OpenAILLM:
    def __init__(self, client: Client, tool_factory: IToolFactoryService):
        self.client = client
        self.tool_factory = tool_factory

        # set default values
        self.API_TIMEOUT = 10
        self.RUN = {
            "TERMINAL_STATES": ["expired", "completed", "failed", "cancelled"],
            "PENDING_STATES": ["queued", "in_progress", "cancelling"],
            "ACTION_STATES": ["requires_action"],
        }

        self._self_update_tools()

    @property
    def source(self):
        return LLMSource.OpenAI

    async def create_assistant(
        self, name: str, instructions: str, model: str
    ) -> AssistantEntity:
        openai_assistant = self.client.beta.assistants.create(
            name=name,
            instructions=instructions,
            tools=self.openai_tools,
            model=model,
        )
        assistant = AssistantEntity(
            id=openai_assistant.id,
            name=openai_assistant.name,
            created_at=datetime.fromtimestamp(openai_assistant.created_at),
            instructions=openai_assistant.instructions,
            model=openai_assistant.model,
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

        openai_assistant = self.client.beta.assistants.update(
            assistant_id=assistant_id,
            name=name,
            instructions=instructions,
            tools=self.openai_tools,
            model=model,
        )
        assistant = AssistantEntity(
            id=openai_assistant.id,
            name=openai_assistant.name,
            created_at=datetime.fromtimestamp(openai_assistant.created_at),
            instructions=openai_assistant.instructions,
            model=openai_assistant.model,
            llmsource=self.source,
        )
        return assistant

    async def delete_assistant(self, assistant_id: str):
        try:
            self.client.beta.assistants.delete(
                assistant_id=assistant_id, timeout=self.API_TIMEOUT
            )
        except Exception as e:
            print(e)
        return

    async def create_thread(
        self, assistant_id: str, default_name: str
    ) -> AssistantThreadEntity:
        openai_thread = self.client.beta.threads.create(
            timeout=self.API_TIMEOUT
        )
        thread = AssistantThreadEntity(
            id=openai_thread.id,
            name=default_name,
            assistant_id=assistant_id,
            created_at=datetime.fromtimestamp(openai_thread.created_at),
        )
        return thread

    async def delete_thread(self, thread_id):
        try:
            self.client.beta.threads.delete(thread_id, timeout=self.API_TIMEOUT)
        except Exception as e:
            print(e)
        return

    async def process_user_message(
        self,
        assistant_id: str,
        thread_id: str,
        message: str,
    ) -> Tuple[AssistantMessageItem, List[AssistantMessageItem]]:
        user_message: AssistantMessageItem = await self._send_message(
            thread_id, message
        )
        responses: List[AssistantMessageItem] | None = await self._get_response(
            assistant_id=assistant_id,
            thread_id=thread_id,
        )
        # if there is something wrong with the thread. TODO !!!IMPORTANT!!!: remove thread from assistants
        if responses is None:
            responses: List[AssistantMessageItem] = [
                AssistantMessageItem(
                    id=f"internal_{str(uuid.uuid4())}",
                    role=Role.Assistant,
                    created_at=datetime.now(),
                    value=AssistantMessageValue(
                        type=AssistantMessageType.Text,
                        content={
                            "message": "There is something wrong with this particular chat. Please, start new chat."
                        },
                    ),
                )
            ]
        user_message_and_responses = [user_message] + responses
        return user_message_and_responses

    async def update_tools(self, assistant_id):
        # update OpenAI Client. TODO: add a check for success
        self.client.beta.assistants.update(
            assistant_id,
            tools=self.openai_tools,
        )

    def _self_update_tools(self):
        # gather tools information
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

    async def _send_message(
        self, thread_id: str, message: str
    ) -> AssistantMessageItem:
        runs = self.client.beta.threads.runs.list(
            thread_id, timeout=self.API_TIMEOUT
        )
        if len(runs.data) > 0:
            run = runs.data[0]
            if run.status not in self.RUN["TERMINAL_STATES"]:
                print(
                    f"[_send_message] Existing run: {run.id}, status: {run.status}"
                )
                try:
                    self.client.beta.threads.runs.cancel(
                        thread_id=thread_id,
                        run_id=run.id,
                        timeout=self.API_TIMEOUT,
                    )
                except Exception as e:
                    print(f"[_send_message] Error cancelling the run: {e}")
                await self._wait_on_run(thread_id, run)
                print(
                    f"[_send_message] After wait | Existing run: {run.id}, status: {run.status}"
                )

        thread_message = self.client.beta.threads.messages.create(
            thread_id,
            role="user",
            content=message,
            timeout=self.API_TIMEOUT,
        )
        print("[_send_message] Sent a message")

        user_message = AssistantMessageItem(
            id=thread_message.id,
            role=Role.User,
            created_at=datetime.now(),
            value=AssistantMessageValue(
                type=AssistantMessageType.Text, content={"message": message}
            ),
        )

        return user_message

    async def _wait_on_run(self, thread_id: str, run: Run) -> Run:
        print(
            f"[_wait_on_run] before id: {run.id} status: {run.status}, error: {run.last_error}"
        )
        itr = 0
        MAX_ITR = 120
        while run.status in self.RUN["PENDING_STATES"] and itr <= MAX_ITR:
            itr += 1
            print(
                f"[_wait_on_run] waiting for id: {run.id} status: {run.status}, error: {run.last_error}"
            )
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id, run_id=run.id, timeout=self.API_TIMEOUT
            )
            time.sleep(0.5)
        print(
            f"[_wait_on_run] after id: {run.id} status: {run.status}, error: {run.last_error}"
        )

        if itr > MAX_ITR:
            try:
                print(f"[_wait_on_run] Cancelling the run {run.id}, itr: {itr}")
                self.client.beta.threads.runs.cancel(
                    thread_id=thread_id, run_id=run.id, timeout=self.API_TIMEOUT
                )
            except Exception as e:
                print(f"[_wait_on_run] Error cancelling the run: {e}")
                run.status = "cancelled"

        return run

    async def _get_response(
        self,
        assistant_id: str,
        thread_id: str,
    ) -> List[AssistantMessageItem] | None:
        # creating a run
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            timeout=self.API_TIMEOUT,
        )

        # set itearions
        itr = 0
        MAX_ITR = 10

        # set frontend_outputs
        frontend_outputs: List[AssistantMessageItem] = []

        # processing the run with or without actions
        while (
            run := await self._wait_on_run(thread_id, run)
        ).status not in self.RUN["TERMINAL_STATES"] and itr <= MAX_ITR:
            itr += 1
            print(f"[_get_response] run.status: {run.status}")
            if run.status != "requires_action":  # doesn't require action!
                continue

            if (
                run.required_action is None
            ):  # run.required_action is not properly defined
                print("[_get_response] run.required_action is None")
                run = self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=[],
                    timeout=self.API_TIMEOUT,
                )

            ###############################
            ####### REQUIRES ACTION #######
            ###############################

            # set tool_outputs for current run tool calling iteration
            tool_outputs = []
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                # process tool_call
                print(
                    f"\n\n[_get_response] executing function {tool_call.function.name}, with args: {tool_call.function.arguments}\n\n"
                )

                # create args for the current tool_call. TODO: improve the logic here
                args = {}
                try:
                    args = json.loads(tool_call.function.arguments)
                except Exception as e:
                    print(f"function argument parsing error: {e}, args: {args}")

                # call tool_function
                (
                    output,
                    new_frontend_contents,
                ) = self.tool_factory.call_tool_function(
                    function_name=tool_call.function.name, args=args
                )

                # print(f"\n\n[_get_response], {output}, {new_frontend_contents}\n\n")
                # save the resulted ouputs
                tool_outputs.append(
                    {"tool_call_id": tool_call.id, "output": output}
                )
                frontend_outputs.extend(new_frontend_contents)

            # submit the results of the tool-functions
            run = self.client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs,
                timeout=self.API_TIMEOUT,
            )

        if itr > MAX_ITR:
            return None

        # prepare the final message from the OpenAI Assistant
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id,
            timeout=self.API_TIMEOUT,
        )
        assistant_message = messages.data[0]

        # for each message, create a value wrapper. TODO: Process content.test is None = MessageContentImageFile or other file/json/etc.
        for content in assistant_message.content:
            if content.text is not None:
                assistant_frontent_output = AssistantMessageItem(
                    id=assistant_message.id,
                    role=Role.Assistant,
                    created_at=datetime.now(),
                    value=AssistantMessageValue(
                        type=AssistantMessageType.Text,
                        content={"message": content.text.value},
                    ),
                )
                frontend_outputs.append(assistant_frontent_output)

        return frontend_outputs


if TYPE_CHECKING:
    _: type[LLM] = OpenAILLM
