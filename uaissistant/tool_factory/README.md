### How to develop tool-function

1. Create class in the file in the folder `tools`.

```
Example:

class get_something_useful(ToolFunction):
    """Returns something useful, which is described as follows..."""

    some_arg_from_openai_assistant: str | int = Field(dsescription="This very useful argument for the very useful Tool-function `get_something_useful`")

    def run(self, tfr: IToolFactoryRepository, **args) -> Tuple[str, List[AssistantMessageValue]]:
        print(f"[{self.__class__.__name__}] args={args}")


        # - DO SOMETHING USEFUL
        # - you can use tfr: ToolFactoryRepository to access the Databases (Postgres and ClickHouse)
        # - use `some_arg_from_openai_assistant` as `self.some_arg_from_openai_assistant`

        # Conclude the output for OpenAI Assistantant and the Glassdome frontent:
        output = f"Here is the result of something useful: ..."
        frontend_values = [AssistantMessageValue(type=AssistantMessageType.Text, content={"message": f"Here is our useful result{}"})]

        print(f"[{self.__class__.__name__}] DONE")

        return output, frontend_values
```

2. Implement the tool-function logic and corresponding outputs for OpenAI Assistant (output) and values for the frontent.

3. Don't forget to write down the description of the tool-function after the ToolFunction defenition and for the required arguments that you would like to get from OpenAI Assistant.

4. Import your function to `tools/__init__.py` as follows: `from .your_file import get_something_useful`

5. Great! After all of these steps, your tool-function can be called by the openAI assistant!
