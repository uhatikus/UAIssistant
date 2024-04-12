from typing import List, Tuple

import pandas as pd

from uaissistant.assistant.models import AssistantMessageValue
from uaissistant.assistant.schemas import AssistantMessageType
from uaissistant.tool_factory.repository import IToolFactoryRepository

from uaissistant.tool_factory.tools.data_analysis.data_analyser import (
    DataAnalyser,
)


class statistics(DataAnalyser):
    """Call this function to give to the user a statistics of the data available"""

    def run(
        self, tfr: IToolFactoryRepository, **args
    ) -> Tuple[str, List[AssistantMessageValue]]:
        print(f"[{self.__class__.__name__}] args={args}")

        # get data
        data: pd.DataFrame = self.get_validated_dataset(tfr, self.dataset_name)
        column_names = data.columns

        # set target_columns
        self.target_columns = self.get_validated_target_columns(
            good_columns=data.select_dtypes(include=["number"])
        )

        # get the data only for target columns
        data = data[self.target_columns]

        ##############################
        ##### from data to stats #####
        ##############################
        stats = data.describe().T  # .T to transpose for similar structure
        stats["25%-quantile"] = data.quantile(0.25)
        stats["median"] = data.quantile(0.5)  # Same as '50%'
        stats["75%-quantile"] = data.quantile(0.75)
        #########################################

        #########################################
        ##### Output the stats to Assistant #####
        #########################################

        output = f"The user has successfully received the statistics. The columns names of this dataset: {column_names}"
        frontend_values = [
            AssistantMessageValue(
                type=AssistantMessageType.Text,
                content={
                    "message": f"The statistics for the columns: {'; '.join(list(self.target_columns))} are as follows:\n\n{stats.to_markdown()}"
                },
            )
        ]

        print(f"[{self.__class__.__name__}] DONE")

        return output, frontend_values
