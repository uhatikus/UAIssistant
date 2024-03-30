from typing import TYPE_CHECKING, Protocol, runtime_checkable

from sqlalchemy.orm import Session


@runtime_checkable
class IToolFactoryRepository(Protocol):
    pass


class ToolFactoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session


if TYPE_CHECKING:
    _: type[IToolFactoryRepository] = ToolFactoryRepository
