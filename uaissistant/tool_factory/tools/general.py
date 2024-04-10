from datetime import datetime
import pytz
from typing import List, Tuple

from pydantic import Field

from uaissistant.assistant.models import AssistantMessageValue
from uaissistant.tool_factory.repository import IToolFactoryRepository
from uaissistant.tool_factory.schemas.tool_function import ToolFunction


class get_current_time(ToolFunction):
    """Returns the current time (by default: in UTC). This function should be used to identify time periods like last day, last week or last month, etc."""

    timezone_str: str = Field(
        default="UTC",
        description="Time zone string for python pytz.timezone",
    )

    def run(
        self, tfr: IToolFactoryRepository, **args
    ) -> Tuple[str, List[AssistantMessageValue]]:
        print(f"[{self.__class__.__name__}] args={args}")

        tz = pytz.timezone(self.timezone_str)

        current_time_str = datetime.now(tz).strftime("%d %b %Y, %H:%M:%S, %Z")

        output = f"The current time is {current_time_str}"
        frontend_values = []

        print(f"[{self.__class__.__name__}] DONE")

        return output, frontend_values
