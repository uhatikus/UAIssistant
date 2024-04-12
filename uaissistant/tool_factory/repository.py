from typing import TYPE_CHECKING, Protocol, runtime_checkable
import pandas as pd

from sqlalchemy.orm import Session
from sqlalchemy.sql import text


@runtime_checkable
class IToolFactoryRepository(Protocol):
    def get_data(self, dataset_name: str) -> pd.DataFrame:
        pass


class ToolFactoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_data(self, dataset_name: str) -> pd.DataFrame:
        query = f"SELECT * FROM {dataset_name}"

        result = self.session.execute(text(query))
        rows = result.fetchall()
        self.session.commit()

        if rows:
            columns = result.keys()
            df = pd.DataFrame(rows, columns=columns)
            return df
        else:
            return pd.DataFrame()


if TYPE_CHECKING:
    _: type[IToolFactoryRepository] = ToolFactoryRepository
