from datetime import datetime, timezone
from typing import List, Tuple

from uaissistant.assistant.models import AssistantMessageValue
from uaissistant.tool_factory.repository import IToolFactoryRepository
from uaissistant.tool_factory.schemas.tool_function import ToolFunction


class get_current_time(ToolFunction):
    """Returns the current time. This function should be used to identify time periods like last day, last week or last month, etc."""

    def run(
        self, tfr: IToolFactoryRepository, **args
    ) -> Tuple[str, List[AssistantMessageValue]]:
        print(f"[{self.__class__.__name__}] ")

        current_time_str = datetime.now(timezone.utc).strftime(
            "%d %b %Y, %H:%M:%S"
        )

        output = f"The current time is {current_time_str}"
        frontend_values = []

        print(f"[{self.__class__.__name__}] DONE")

        return output, frontend_values
