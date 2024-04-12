from typing import List, Tuple
import uuid

import numpy as np
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from pydantic import Field
from uaissistant.assistant.models import AssistantMessageValue
from uaissistant.assistant.schemas import AssistantMessageType
from uaissistant.tool_factory.repository import IToolFactoryRepository

from uaissistant.tool_factory.tools.data_analysis.data_analyser import (
    DataAnalyser,
)

import plotly.express as px


class histogram(DataAnalyser):
    """Call this function to give to the user a histogram plot of the data available"""

    colors: List[str] = Field(
        default=px.colors.qualitative.Set1,
        description="List of colors to use. Example: ['rgb(228,26,28)', 'rgb(55,126,184)', 'rgb(77,175,74)']. Applied in same order as target_columns List.",
    )

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

        #############################
        ##### from data to plot #####
        #############################
        rows, cols = 1, 1
        specs = [[{}]]

        if len(data.columns) > 1:
            rows, cols = int(len(data.columns) / 2), 2
            specs = [[{}, {}] for _ in range(rows)]

            if len(data.columns) % 2:
                rows = rows + 1
                specs.append([{}, None])

        print(f"[{self.__class__.__name__}] rows and cols: {rows}, {cols}")
        fig = make_subplots(rows=rows, cols=cols, print_grid=True)

        for i in range(rows):
            for j in range(cols):
                if specs[i][j] is None:
                    break
                idx = i * 2 + j
                fig.add_trace(
                    go.Histogram(
                        x=data.iloc[:, idx],
                        name=data.columns[idx],
                        marker_color=self.colors[idx],
                    ),
                    row=i + 1,
                    col=j + 1,
                )
        # Update layout
        fig.update_layout(title=self.dataset_name)
        ########################################

        ########################################
        ##### Output the plot to Assistant #####
        ########################################

        fig_json = fig.to_json()

        output = f"The user has successfully received the histogram plot. The columns names of this dataset: {column_names}"
        file_id = f"{self.__class__.__name__}_{str(uuid.uuid4())}"
        filename = f"{file_id}.json"
        frontend_values = [
            AssistantMessageValue(
                type=AssistantMessageType.Plot,
                content={
                    "file_id": file_id,
                    "filename": filename,
                    "raw_json": fig_json,
                },
            )
        ]

        print(f"[{self.__class__.__name__}] DONE")

        return output, frontend_values


class correlation_heatmap(DataAnalyser):
    """Call this function to give to the user a correlation heatmap plot of the data available"""

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

        #############################
        ##### from data to plot #####
        #############################
        data_corr: pd.DataFrame = data.corr()
        fig = go.Figure()
        fig.add_trace(
            go.Heatmap(
                x=data_corr.columns,
                y=data_corr.index,
                z=np.array(data_corr),
                colorscale=self.colorscale,  # Choose a color scale
                colorbar=dict(
                    title="Correlation"
                ),  # Add a color bar with a title
                zmax=1,
                zmin=-1,
            )
        )
        fig.update_layout(
            title=f"Correlation Heatmap for {self.dataset_name}",
            height=600,  # Adjust the height of the figure
            width=600,  # Adjust the width of the figure
            yaxis=dict(autorange="reversed"),
        )
        ########################################

        ########################################
        ##### Output the plot to Assistant #####
        ########################################

        fig_json = fig.to_json()

        output = f"The user has successfully received the correlation heatmap plot. The columns names of this dataset: {column_names}"
        file_id = f"{self.__class__.__name__}_{str(uuid.uuid4())}"
        filename = f"{file_id}.json"
        frontend_values = [
            AssistantMessageValue(
                type=AssistantMessageType.Plot,
                content={
                    "file_id": file_id,
                    "filename": filename,
                    "raw_json": fig_json,
                },
            )
        ]

        print(f"[{self.__class__.__name__}] DONE")

        return output, frontend_values


class correlation_scatter_plot(DataAnalyser):
    """Call this function to give to the user a correlation scatter plot plot of the data available. Set exactly 2 target_columns."""

    trendline_color: str = Field(
        default="red",
        description="Color for trendline. Examples: 'rgb(228,26,28)', 'rgb(55,126,184)', 'rgb(77,175,74)'.",
    )
    trendline_style: str = Field(
        default="dash", description="'dash', 'dot', or 'dashdot'"
    )

    colors: List[str] = Field(
        default=px.colors.qualitative.Set1,
        description="List of colors to use. Example: ['rgb(228,26,28)', 'rgb(55,126,184)', 'rgb(77,175,74)']. Applied in same order as target_columns List.",
    )

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

        if len(self.target_columns) != 2:
            raise Exception(
                "target_columns does not have exactly 2 columns! Exactly 2 numerical columns are required!"
            )

        # get the data only for target columns
        data = data[self.target_columns]

        #############################
        ##### from data to plot #####
        #############################
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=data.iloc[:, 0],
                y=data.iloc[:, 1],
                mode="markers",
                marker=dict(
                    color=self.colors[0],  # Use another column for color
                ),
            )
        )
        # Add trendline
        fig.add_trace(
            go.Scatter(
                x=data.iloc[:, 0],
                y=np.poly1d(np.polyfit(data.iloc[:, 0], data.iloc[:, 1], 1))(
                    data.iloc[:, 0]
                ),
                mode="lines",
                line=dict(
                    color=self.trendline_color, dash=self.trendline_style
                ),  # Customize line color and style
                name="Trendline",  # Specify trace name for legend
            )
        )
        # Show trendline equation as annotation
        coefficients = np.polyfit(data.iloc[:, 0], data.iloc[:, 1], 1)
        equation = f"y = {coefficients[0]:.2f}x + {coefficients[1]:.2f}"

        fig.update_layout(
            title=f"Correlation Scatter Plot: {equation}",
            xaxis_title=data.columns[0],
            yaxis_title=data.columns[1],
            xaxis=dict(
                showgrid=True, gridcolor="lightgray"
            ),  # Specify grid color for x-axis
            yaxis=dict(showgrid=True, gridcolor="lightgray"),
        )
        ########################################

        ########################################
        ##### Output the plot to Assistant #####
        ########################################

        fig_json = fig.to_json()

        output = f"The user has successfully received the correlation scatter plot. The columns names of this correlation scatter plot: {column_names}"
        file_id = f"{self.__class__.__name__}_{str(uuid.uuid4())}"
        filename = f"{file_id}.json"
        frontend_values = [
            AssistantMessageValue(
                type=AssistantMessageType.Plot,
                content={
                    "file_id": file_id,
                    "filename": filename,
                    "raw_json": fig_json,
                },
            )
        ]

        print(f"[{self.__class__.__name__}] DONE")

        return output, frontend_values
