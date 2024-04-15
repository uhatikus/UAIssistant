### How to add LLM

1. If possible, create a module for your LLM connection. You can check the examples: [OpenAI's ChatGPT](../connections/openaix/__init__.py) and [Anthropic's Claude](../connections/anthropicx/__init__.py)

2. Create folder `llm_name` in the folder `uaissistant/llms` with files `__init__.py` and `llm_name.py`.

3. Follow the protocol from [llm.py](llm.py) to implement `you llm class`. You can use `openai`, `anthropic` and `gemini` as an example.

```
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

    async def delete_assistant(self, assistant_id: str):
        pass

    async def create_thread(
        self, assistant_id: str, default_name: str
    ) -> AssistantThreadEntity:
        pass

    async def delete_thread(self, thread_id: str):
        pass

    async def process_user_message(
        self,
        assistant: AssistantEntity,
        thread_id: str,
        message: str,
    ) -> List[AssistantMessageItem]:
        pass

    async def update_tools(self, assistant_id: str):
        pass

```

4. Add you_llm_schema to [tool-function.py](../tool_factory/schemas/tool_function.py) for a proper tool-function calling.

5. Add your llm class to the [LLM module](module.py)

6. Add all created modules to the [main.py](../main.py)

7. Add required env variablee to the [.env](../../.env) and [.env.example](../../.env) files

8. Great! After all of these steps you will be able to use your LLM!
