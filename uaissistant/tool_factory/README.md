### How to develop tool-function

1. Create class in the file in the folder `uaissistant/tool_factory/tools`.

```
Example:

class get_something_useful(ToolFunction):
    """Returns something useful, which is described as follows..."""

    some_arg_from_llm: str | int = Field(dsescription="This very useful argument for the very useful Tool-function `get_something_useful`")

    def run(self, tfr: IToolFactoryRepository, **args) -> Tuple[str, List[AssistantMessageValue]]:
        print(f"[{self.__class__.__name__}] args={args}")


        # - DO SOMETHING USEFUL
        # - you can use tfr: ToolFactoryRepository to access the Databases (Postgres and ClickHouse)
        # - use `some_arg_from_llm` as `self.some_arg_from_llm`
        # - create plotly fig that can be converted to the json file

        # Conclude the output for LLM:
        output = f"Here is the result of something useful: ..."

        # Conclude the output for the frontent:
        fig_json = fig.to_json()
        file_id = f"{self.__class__.__name__}_{str(uuid.uuid4())}"
        filename = f"{file_id}.json"
        frontend_values = [
            AssistantMessageValue(
                type=AssistantMessageType.Text,
                content={
                    "message": f"Here is our useful result: {result}"
                },
            ),
            AssistantMessageValue(
                type=AssistantMessageType.Plot,
                content={
                    "file_id": file_id,
                    "filename": filename,
                    "raw_json": fig_json,
                },
            ),
        ]

        print(f"[{self.__class__.__name__}] DONE")

        return output, frontend_values
```

2. Implement the tool-function logic and corresponding _outputs for the LLMs_ and _values for the frontent_.

3. Don't forget to write down the description of the tool-function after the ToolFunction defenition and for the required arguments that you would like to get from LLM.

4. Import your function to `tools/__init__.py` as follows: `from .your_file import get_something_useful`

5. Great! After all of these steps, your tool-function can be called by all the LLMs including OpenAI's ChatGPT, Anthropic's Claude and Google's Gemini!
