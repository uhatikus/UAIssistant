from abc import abstractmethod
from typing import List, Tuple, Any

import pandas as pd
from pydantic import Field
from uaissistant.assistant.models import AssistantMessageValue
from uaissistant.tool_factory.repository import IToolFactoryRepository
from uaissistant.tool_factory.schemas.tool_function import ToolFunction


class DataAnalyser(ToolFunction):
    """DataAnalyser Class"""

    dataset_name: str = Field(
        description="The name of the dataset to analize.",
    )

    target_columns: List[str] = Field(
        default=None,
        description="The columns of the dataset that the user would like to plot. By default, this function will use all available columns in the dataset.",
    )

    colorscale: str = Field(
        default="RdBu_r",
        description="Colorscale for plotly plots. Example: 'RdBu_r'",
    )

    @abstractmethod
    def run(
        self, tfr: IToolFactoryRepository, **args: Any
    ) -> Tuple[str, List[AssistantMessageValue]]:
        pass

    def get_validated_dataset(
        self, tfr: IToolFactoryRepository, dataset_name
    ) -> Any:
        # get data
        data: pd.DataFrame = tfr.get_data(dataset_name)

        if len(data.columns) == 0:
            raise Exception("The chosen dataset is empty!")

        # extract different types of columns
        numerical_columns = data.select_dtypes(include=["number"])
        # categorical_columns = data.select_dtypes(include=["category", "object"])

        # set target_columns
        self.target_columns = (
            numerical_columns
            if self.target_columns is None
            else self.target_columns
        )

        # validate columns
        self.target_columns = [
            col for col in self.target_columns if col in numerical_columns
        ]

        return data

    def get_validated_target_columns(self, good_columns) -> Any:
        # good_columns examples
        # numerical_columns = data.select_dtypes(include=["number"])
        # categorical_columns = data.select_dtypes(include=["object"])

        if self.target_columns is None:
            return good_columns
        else:
            return [col for col in self.target_columns if col in good_columns]
