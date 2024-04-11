import pandas as pd
import numpy as np

from sklearn.datasets import load_iris
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


def get_iris_dataset():
    # Load Iris dataset
    iris = load_iris()

    # Convert the dataset into a Pandas DataFrame
    iris_df = pd.DataFrame(data=iris["data"], columns=iris["feature_names"])

    # Add target names to the DataFrame
    iris_df["target"] = iris["target"]

    # Replace numerical target values with their corresponding target names
    iris_df["target"] = iris_df["target"].replace(
        {0: "Iris-setosa", 1: "Iris-versicolor", 2: "Iris-virginica"}
    )
    return iris_df


def categorical_modeling(data, features, target):
    X = data[features]
    y = data[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.94, random_state=42
    )

    numeric_features = X_train.select_dtypes(include=["number"]).columns
    categorical_features = X_train.select_dtypes(include=["object"]).columns

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

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier()),
        ]
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

    # Compute confusion matrix
    cm = confusion_matrix(y_test, y_pred)

    print(y_test, y_test.unique())
    # Create labels for x and y axes
    labels = [f"Predicted {col}" for col in y_test.unique()]
    y_labels = [f"Actual {col}" for col in y_test.unique()]

    # Create confusion matrix heatmap
    fig = ff.create_annotated_heatmap(
        z=cm,
        x=labels,
        y=y_labels,
        colorscale="Blues",
    )

    # Add title
    fig.update_layout(
        xaxis=dict(title="Predicted label"),
        yaxis=dict(title="True label"),
    )

    # Show the plot
    fig.show()


def numerical_modeling(data, features, target):
    X = data[features]
    y = data[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    numeric_features = X_train.select_dtypes(include=["number"]).columns
    categorical_features = X_train.select_dtypes(include=["object"]).columns

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
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", RandomForestRegressor()),
        ]
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("Mean Squared Error:", mean_squared_error(y_test, y_pred))
    print("R^2 Score:", r2_score(y_test, y_pred))

    # Plot predicted vs actual
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=y_test,
            y=y_pred,
            mode="markers",
            name="Predicted vs Actual",
            marker=dict(color="blue"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[y_test.min(), y_test.max()],
            y=[y_test.min(), y_test.max()],
            mode="lines",
            name="Perfect Prediction",
            line=dict(color="black", dash="dash"),
        )
    )
    fig.update_layout(
        xaxis_title="Actual",
        yaxis_title="Predicted",
        title="Actual vs Predicted",
    )
    fig.show()

    # Get feature importances
    importances = model.named_steps["regressor"].feature_importances_

    # Get numerical feature names
    numeric_feature_names = numeric_features.tolist()

    # Get categorical feature names after one-hot encoding
    categorical_feature_names = (
        model.named_steps["preprocessor"]
        .transformers_[1][1]
        .named_steps["onehot"]
        .get_feature_names_out(categorical_features)
    )

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
                start_index : start_index + len(categorical_feature_names[i])
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
    sorted_feature_names, sorted_importances = zip(*sorted_features_importances)
    # Create a bar plot for feature importances
    importance_fig = go.Figure()
    importance_fig.add_trace(
        go.Bar(
            x=sorted_feature_names,
            y=sorted_importances,
            marker=dict(color="blue"),
        )
    )
    importance_fig.update_layout(
        title="Feature Importances",
        xaxis_title="Features",
        yaxis_title="Importance",
    )
    importance_fig.show()


if __name__ == "__main__":
    data = get_iris_dataset()
    features = [
        "sepal length (cm)",
        "sepal width (cm)",
        "petal length (cm)",
        "petal width (cm)",
    ]
    target = "target"
    categorical_modeling(data, features, target)
    features = [
        "sepal width (cm)",
        "petal length (cm)",
        "petal width (cm)",
        "target",
    ]
    target = "sepal length (cm)"
    numerical_modeling(data, features, target)
