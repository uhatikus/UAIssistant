from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Type, TypeVar

from uaissistant.assistant.models import AssistantMessageValue
from uaissistant.tool_factory.repository import IToolFactoryRepository
from pydantic import BaseModel

F = TypeVar("F", bound="ToolFunction")

# https://medium.com/dev-bits/a-clear-guide-to-openai-function-calling-with-python-dcbc200c5d70


class ToolFunction(BaseModel, ABC):
    class Metadata:
        subclasses: List[Type[F]] = []

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any):
        pass
        super().__pydantic_init_subclass__(**kwargs)
        _schema = cls.model_json_schema()
        if cls.__doc__ is None:
            raise ValueError(
                f"OpenAIFunction subclass {cls.__name__} must have a docstring"
            )
        cls.openaischema = {
            "name": cls.__name__,
            "description": cls.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    k: v
                    for k, v in _schema["properties"].items()
                    if k != "self"
                },
                "required": list(_schema["required"])
                if "required" in _schema
                else [],
            },
        }
        cls.Metadata.subclasses.append(cls)

    def __call__(
        self, tfr: IToolFactoryRepository, args: Any
    ) -> Tuple[str, List[AssistantMessageValue]]:
        return self.run(tfr, **args)

    @abstractmethod
    def run(
        self, tfr: IToolFactoryRepository, **args: Any
    ) -> Tuple[str, List[AssistantMessageValue]]:
        ...