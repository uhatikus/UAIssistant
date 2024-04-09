from typing import TYPE_CHECKING, List, Protocol, runtime_checkable

from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from uaissistant.assistant.schemas import AssistantMessageEntity


@runtime_checkable
class IAnthropicRepository(Protocol):
    async def list_old_messages(
        self, thread_id: str
    ) -> List[AssistantMessageEntity]:
        pass


class AnthropicRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    async def list_old_messages(
        self, thread_id: str
    ) -> List[AssistantMessageEntity]:
        query = """
        SELECT id, assistant_id, thread_id, created_at, role, type, content FROM assistant_message
        WHERE thread_id = :thread_id
        """
        parameters = {
            "thread_id": thread_id,
        }

        rows = self.session.execute(text(query), parameters).fetchall()
        self.session.commit()

        return [AssistantMessageEntity(*row) for row in rows]


if TYPE_CHECKING:
    _: type[IAnthropicRepository] = AnthropicRepository
