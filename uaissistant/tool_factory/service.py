import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Protocol, Tuple, runtime_checkable

from uaissistant.assistant.models import AssistantMessageItem
from uaissistant.assistant.schemas import Role
from uaissistant.tool_factory.repository import IToolFactoryRepository

from . import tools


@runtime_checkable
class IToolFactoryService(Protocol):
    def call_tool_function(
        function_name: str, args: dict[str, Any]
    ) -> Tuple[str, List[AssistantMessageItem]]:
        pass

    def get_tools() -> dict[str, Any]:
        pass


class ToolFactoryService:
    def __init__(self, tfr: IToolFactoryRepository) -> None:
        self.tfr = tfr

    def call_tool_function(
        self, function_name: str, args: dict[str, Any]
    ) -> Tuple[str, List[AssistantMessageItem]]:
        output = ""
        frontend_values = []
        try:
            function_object = getattr(tools, function_name)
            function_object_initialized = function_object(**args)
            # Check if the object is callable (a function/method)
            if callable(function_object):
                output, frontend_values = function_object_initialized(
                    tfr=self.tfr, args=args
                )
            else:
                output = f"The function '{function_name}' does not exist in the module."
                print(f"[{self.__class__.__name__}] {output}")
        except Exception as e:
            output = f"Error running the function {function_name}. Error {e}. Consider to stop calling this function if you have tried more than 3 times."
            print(f"[{self.__class__.__name__}] {output}")

        frontend_contents = [
            AssistantMessageItem(
                id=f"internal_{str(uuid.uuid4())}",
                role=Role.Assistant,
                created_at=datetime.now(),
                value=value,
            )
            for value in frontend_values
        ]

        return output, frontend_contents


if TYPE_CHECKING:
    _: type[IToolFactoryService] = ToolFactoryService
