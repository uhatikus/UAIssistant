from typing import List, Tuple

from pydantic import Field

from uaissistant.assistant.models import AssistantMessageValue
from uaissistant.assistant.schemas import AssistantMessageType
from uaissistant.tool_factory.repository import IToolFactoryRepository
from uaissistant.tool_factory.schemas.tool_function import ToolFunction

import subprocess


class execute_bash_scripts(ToolFunction):
    """Executes the given bash script and return the result"""

    bash_scrit: List[str] = Field(
        default=None,
        description="Bash scripts is a list of words of the bash script that can be executed by subprocess.check_output function",
    )

    def run(
        self, tfr: IToolFactoryRepository, **args
    ) -> Tuple[str, List[AssistantMessageValue]]:
        print(f"[{self.__class__.__name__}] args={args} ")

        result = str(subprocess.check_output(self.bash_scrit), "utf8")

        output = "The bash script is executed. Just tell the user that the result is ready"
        frontend_values = [
            AssistantMessageValue(
                type=AssistantMessageType.Text,  # noqa: F821
                content={
                    "message": f"The Script output is the following:\n {result}"
                },
            )
        ]

        print(f"[{self.__class__.__name__}] DONE")

        return output, frontend_values
