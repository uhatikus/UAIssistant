from typing import List, Tuple

import pandas as pd
from pydantic import Field

from uaissistant.assistant.models import AssistantMessageValue
from uaissistant.tool_factory.repository import IToolFactoryRepository
from uaissistant.tool_factory.schemas.tool_function import ToolFunction


DATASETS = ["iris", "diabetes"]


class get_datasets(ToolFunction):
    """Returns the list of available datasets names for analysis."""

    def run(
        self, tfr: IToolFactoryRepository, **args
    ) -> Tuple[str, List[AssistantMessageValue]]:
        print(f"[{self.__class__.__name__}] args={args}")

        output = f"List of available datasets name: {DATASETS}"
        frontend_values = []

        print(f"[{self.__class__.__name__}] DONE")

        return output, frontend_values


class get_dataset_columns(ToolFunction):
    """Returns the list of the columns in the given dataset and the number of rows."""

    dataset_name: str = Field(
        description="The name of the dataset to analize.",
    )

    def run(
        self, tfr: IToolFactoryRepository, **args
    ) -> Tuple[str, List[AssistantMessageValue]]:
        print(f"[{self.__class__.__name__}] args={args}")

        # get data
        data: pd.DataFrame = tfr.get_data(self.dataset_name)

        if len(data.columns) == 0:
            raise Exception("The chosen dataset is empty!")

        output = f"The dataset {self.dataset_name} contains the following columns: {data.columns} (with the following types: {data.dtypes}). There are {len(data)} rows in total."
        frontend_values = []

        print(f"[{self.__class__.__name__}] DONE")

        return output, frontend_values
