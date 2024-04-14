from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Type, TypeVar

from uaissistant.assistant.models import AssistantMessageValue
from uaissistant.tool_factory.repository import IToolFactoryRepository
from pydantic import BaseModel

import google.ai.generativelanguage as glm

F = TypeVar("F", bound="ToolFunction")

# https://medium.com/dev-bits/a-clear-guide-to-openai-function-calling-with-python-dcbc200c5d70

type2glmtype = {
    "string": glm.Type.STRING,
    "number": glm.Type.NUMBER,
    "integer": glm.Type.INTEGER,
    "boolean": glm.Type.BOOLEAN,
    "array": glm.Type.ARRAY,
    "object": glm.Type.OBJECT,
}


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
                f"ToolFunction subclass {cls.__name__} must have a docstring"
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
        cls.anthropicschema = {
            "name": cls.__name__,
            "description": cls.__doc__,
            "input_schema": {
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
        cls.geminischema = glm.FunctionDeclaration(
            name=cls.__name__,
            description=cls.__doc__,
            parameters=glm.Schema(
                type=glm.Type.OBJECT,
                properties={
                    k: glm.Schema(
                        type=type2glmtype.get(
                            v["type"], glm.Type.TYPE_UNSPECIFIED
                        ),
                        description=f"{v['description']}.{' Default value: ' + str(v['default']) if 'default' in v else ''}",
                    )
                    for k, v in _schema["properties"].items()
                    if k != "self"
                },
                required=list(_schema["required"])
                if "required" in _schema
                else [],
            ),
        )
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
