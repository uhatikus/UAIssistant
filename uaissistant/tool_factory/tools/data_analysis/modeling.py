from typing import List, Tuple
import uuid
from pydantic import Field

import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_squared_error,
    accuracy_score,
    classification_report,
    r2_score,
    confusion_matrix,
)
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

import plotly.graph_objects as go
import plotly.figure_factory as ff

from uaissistant.assistant.models import AssistantMessageValue
from uaissistant.assistant.schemas import AssistantMessageType
from uaissistant.tool_factory.repository import IToolFactoryRepository

from uaissistant.tool_factory.tools.data_analysis.data_analyser import (
    DataAnalyser,
)


class modeling(DataAnalyser):
    """Call this function to preform modeling for the given dataset"""

    features: List[str] = Field(
        description="The columns of the dataset that will be used as a features for the modeling.",
    )

    target: str = Field(
        description="The column of the dataset that will be used as a target for the modeling.",
    )

    test_size: float = Field(
        default=0.2,
        description="The size of the test dataset for the modeling. The size of the training dataset is (1-test_size)",
    )

    predicted_vs_actual_plot_predicted_color: str = Field(
        default="blue",
        description="Color for `predicted vs actual plot` for predicted points. Examples: 'black', 'green', 'rgb(228,26,28)', 'rgb(55,126,184)', 'rgb(77,175,74)'.",
    )

    predicted_vs_actual_plot_idealcase_color: str = Field(
        default="red",
        description="Color for `predicted vs actual plot` for ideal case line. Examples: 'black', 'green', 'rgb(228,26,28)', 'rgb(55,126,184)', 'rgb(77,175,74)'.",
    )

    importances_bars_color: str = Field(
        default="blue",
        description="Color for importances coeficients bars. Examples: 'black', 'green', 'rgb(228,26,28)', 'rgb(55,126,184)', 'rgb(77,175,74)'.",
    )

    def run(
        self, tfr: IToolFactoryRepository, **args
    ) -> Tuple[str, List[AssistantMessageValue]]:
        print(f"[{self.__class__.__name__}] args={args}")

        # get data
        data: pd.DataFrame = self.get_validated_dataset(tfr, self.dataset_name)

        ####################
        ##### Modeling #####
        ####################

        text_outputs = []
        fig_outputs = []
        if self.target in data.select_dtypes(include=["object"]):
            text_outputs, fig_outputs = self._categorical_modeling(data)
        if self.target in data.select_dtypes(include=["number"]):
            text_outputs, fig_outputs = self._numerical_modeling(data)

        if len(text_outputs) == 0 and len(fig_outputs) == 0:
            raise Exception(
                f"Target '{self.target}' is not a column with type a number or object. The modelling is not supported for this column"
            )

        #########################################

        #########################################
        ##### Output the model to Assistant #####
        #########################################

        output = "The user has successfully received the model outputs."
        features_string = "; ".join(self.features)
        frontend_values = [
            AssistantMessageValue(
                type=AssistantMessageType.Text,
                content={
                    "message": f"Modeling of {self.dataset_name} dataset.\n\nTarget columns is {self.target}.\n\nFeatures are the following:\n\n{features_string}"
                },
            )
        ]
        for fig in fig_outputs:
            fig_json = fig.to_json()
            file_id = f"{self.__class__.__name__}_{str(uuid.uuid4())}"
            filename = f"{file_id}.json"
            frontend_values.append(
                AssistantMessageValue(
                    type=AssistantMessageType.Plot,
                    content={
                        "file_id": file_id,
                        "filename": filename,
                        "raw_json": fig_json,
                    },
                )
            )

        final_message = ("\n\n").join(text_outputs)
        frontend_values.append(
            AssistantMessageValue(
                type=AssistantMessageType.Text,
                content={"message": f"{final_message}"},
            )
        )

        print(f"[{self.__class__.__name__}] DONE")

        return output, frontend_values

    def _categorical_modeling(self, data):
        X = data[self.features]
        y = data[self.target]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size
        )

        numeric_features = X_train.select_dtypes(include=["number"]).columns
        categorical_features = X_train.select_dtypes(include=["object"]).columns

        preprocessor = self._get_preprocessor(
            numeric_features, categorical_features
        )

        model = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("classifier", RandomForestClassifier()),
            ]
        )

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        accuracy_score_result = f"Accuracy: {accuracy_score(y_test, y_pred)}"
        classification_report_result = f"Classification Report:\n\n{classificationreport2dataframe(classification_report(y_test, y_pred, output_dict=True)).to_markdown()}"

        confusion_matrix_fig = self._get_confusion_matrix_plot(y_test, y_pred)

        # Get importance values
        importances = model.named_steps["classifier"].feature_importances_
        model_preprocessor = model.named_steps["preprocessor"]

        importances_fig = self._get_importance_plot(
            importances,
            model_preprocessor,
            numeric_features,
            categorical_features,
        )

        text_outputs = [accuracy_score_result, classification_report_result]
        fig_outputs = [confusion_matrix_fig, importances_fig]

        return text_outputs, fig_outputs

    def _get_confusion_matrix_plot(self, y_test, y_pred):
        # Compute confusion matrix
        cm = confusion_matrix(y_test, y_pred)

        # Create labels for x and y axes
        labels = [f"Predicted {col}" for col in y_test.unique()]
        y_labels = [f"Actual {col}" for col in y_test.unique()]

        # Create confusion matrix heatmap
        fig = ff.create_annotated_heatmap(
            z=cm,
            x=labels,
            y=y_labels,
            colorscale=self.colorscale,
        )

        # Add title
        fig.update_layout(
            xaxis=dict(title="Predicted label"),
            yaxis=dict(title="True label"),
        )

        return fig

    def _numerical_modeling(self, data):
        X = data[self.features]
        y = data[self.target]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size
        )

        numeric_features = X_train.select_dtypes(include=["number"]).columns
        categorical_features = X_train.select_dtypes(include=["object"]).columns

        preprocessor = self._get_preprocessor(
            numeric_features, categorical_features
        )

        model = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("regressor", RandomForestRegressor()),
            ]
        )

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        mean_squared_error_result = (
            f"Mean Squared Error: {mean_squared_error(y_test, y_pred)}"
        )
        r2_score_result = f"R^2 Score: {r2_score(y_test, y_pred)}"

        predict_vs_actual_fig = self._get_predicted_vs_actual_plot(
            y_test, y_pred
        )
        # Get importance values
        importances = model.named_steps["regressor"].feature_importances_
        model_preprocessor = model.named_steps["preprocessor"]

        importances_fig = self._get_importance_plot(
            importances,
            model_preprocessor,
            numeric_features,
            categorical_features,
        )

        text_outputs = [mean_squared_error_result, r2_score_result]
        fig_outputs = [predict_vs_actual_fig, importances_fig]
        return text_outputs, fig_outputs

    def _get_preprocessor(self, numeric_features, categorical_features):
        numerical_pipeline = Pipeline(
            [
                ("imputer", SimpleImputer(strategy="mean")),
                ("scaler", StandardScaler()),
            ]
        )

        categorical_pipeline = Pipeline(
            [
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore")),
            ]
        )

        preprocessor = ColumnTransformer(
            [
                ("num", numerical_pipeline, numeric_features),
                ("cat", categorical_pipeline, categorical_features),
            ]
        )

        return preprocessor

    def _get_predicted_vs_actual_plot(self, y_test, y_pred):
        # Plot predicted vs actual
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=y_test,
                y=y_pred,
                mode="markers",
                name="Predicted vs Actual",
                marker=dict(
                    color=self.predicted_vs_actual_plot_predicted_color
                ),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[y_test.min(), y_test.max()],
                y=[y_test.min(), y_test.max()],
                mode="lines",
                name="Perfect Prediction",
                line=dict(
                    color=self.predicted_vs_actual_plot_idealcase_color,
                    dash="dash",
                ),
            )
        )
        fig.update_layout(
            xaxis_title="Actual",
            yaxis_title="Predicted",
            title="Actual vs Predicted",
        )

        return fig

    def _get_importance_plot(
        self,
        importances,
        model_preprocessor,
        numeric_features,
        categorical_features,
    ):
        # Get numerical feature names
        numeric_feature_names = numeric_features.tolist()

        # Get categorical feature names after one-hot encoding
        try:
            categorical_feature_names = (
                model_preprocessor.transformers_[1][1]
                .named_steps["onehot"]
                .get_feature_names_out(categorical_features)
            )
        except Exception:
            categorical_feature_names = []

        # Combine the numerical and categorical feature importances
        combined_importances = []
        combined_feature_names = []

        # Add numerical feature importances
        combined_importances.extend(importances[: len(numeric_feature_names)])
        combined_feature_names.extend(numeric_feature_names)

        # Add combined importances for categorical features
        start_index = len(numeric_feature_names)
        for i, category in enumerate(categorical_features):
            category_importance = np.sum(
                importances[
                    start_index : start_index
                    + len(categorical_feature_names[i])
                ]
            )
            combined_importances.append(category_importance)
            combined_feature_names.append(category)

        # Zip feature names and importances, and sort them based on importances
        sorted_features_importances = sorted(
            zip(combined_feature_names, combined_importances),
            key=lambda x: x[1],
            reverse=True,
        )

        # Unzip the sorted feature names and importances
        sorted_feature_names, sorted_importances = zip(
            *sorted_features_importances
        )
        # Create a bar plot for feature importances
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=sorted_feature_names,
                y=sorted_importances,
                marker=dict(color=self.importances_bars_color),
            )
        )
        fig.update_layout(
            title="Feature Importances",
            xaxis_title="Features",
            yaxis_title="Importance",
        )
        return fig


def classificationreport2dataframe(report):
    df_classification_report = pd.DataFrame(report).transpose()
    df_classification_report = df_classification_report.sort_values(
        by=["f1-score"], ascending=False
    )
    return df_classification_report
