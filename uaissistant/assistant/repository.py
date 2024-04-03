import json
from typing import TYPE_CHECKING, List, Protocol

from uaissistant.assistant.models import AssistantMessageItem
from uaissistant.assistant.schemas import (
    AssistantEntity,
    AssistantMessageEntity,
    AssistantThreadEntity,
)
from sqlalchemy.orm import Session
from sqlalchemy.sql import text


class IAssistantRepository(Protocol):
    # READ
    async def get_assistant(self, assistant_id: str) -> AssistantEntity | None:
        pass

    async def list_assistants(self) -> List[AssistantEntity]:
        pass

    async def list_threads(
        self, assistant_id: str
    ) -> List[AssistantThreadEntity]:
        pass

    async def list_messages(
        self, thread_id: str
    ) -> List[AssistantMessageEntity]:
        pass

    # CREATE
    async def create_assistant(
        self, assistant: AssistantEntity
    ) -> AssistantEntity | None:
        pass

    async def create_thread(
        self, thread: AssistantThreadEntity
    ) -> AssistantThreadEntity | None:
        pass

    async def add_messages(
        self,
        assistant_id: str,
        thread_id: str,
        messages: List[AssistantMessageItem],
    ) -> List[AssistantMessageEntity]:
        pass

    # DELETE
    async def delete_assistant(
        self, assistant_id: str
    ) -> AssistantEntity | None:
        pass

    async def delete_thread(
        self, thread_id: str
    ) -> AssistantThreadEntity | None:
        pass

    # UPDATE
    async def update_assistant(
        self,
        assistant_id,
        name,
        instructions,
        model,
    ) -> AssistantEntity | None:
        pass

    async def update_thread(
        self, thread_id: str, name: str
    ) -> AssistantThreadEntity | None:
        pass


class AssistantRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # READ
    async def get_assistant(self, assistant_id: str) -> AssistantEntity | None:
        query = "SELECT id, name, created_at, instructions, model, llmsource FROM assistant WHERE id = :assistant_id"
        parameters = {"assistant_id": assistant_id}

        row = self.session.execute(text(query), parameters).fetchone()
        self.session.commit()

        return AssistantEntity(*row) if row is not None else None

    async def list_assistants(self) -> List[AssistantEntity]:
        query = "SELECT id, name, created_at, instructions, model, llmsource FROM assistant"

        rows = self.session.execute(text(query)).fetchall()
        self.session.commit()

        return [AssistantEntity(*row) for row in rows]

    async def list_threads(
        self, assistant_id: str
    ) -> List[AssistantThreadEntity]:
        query = "SELECT id, name, assistant_id, created_at FROM assistant_thread WHERE assistant_id = :assistant_id"
        parameters = {"assistant_id": assistant_id}

        rows = self.session.execute(text(query), parameters).fetchall()
        self.session.commit()

        return [AssistantThreadEntity(*row) for row in rows]

    async def list_messages(
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

    # CREATE
    async def create_assistant(
        self, assistant: AssistantEntity
    ) -> AssistantEntity | None:
        query = """
        INSERT INTO assistant (id, name, created_at, instructions, model, llmsource)
        VALUES (:id, :name, :created_at, :instructions, :model, :llmsource)
        RETURNING id, name, created_at, instructions, model, llmsource
        """
        parameters = {
            "id": assistant.id,
            "name": assistant.name,
            "created_at": assistant.created_at,
            "instructions": assistant.instructions,
            "model": assistant.model,
            "llmsource": assistant.llmsource.value,
        }

        row = self.session.execute(text(query), parameters).fetchone()
        self.session.commit()

        return AssistantEntity(*row) if row is not None else None

    async def create_thread(
        self, thread: AssistantThreadEntity
    ) -> AssistantThreadEntity | None:
        query = """
        INSERT INTO assistant_thread (id, name, assistant_id, created_at)
        VALUES (:id, :name, :assistant_id, :created_at)
        RETURNING id, name, assistant_id, created_at
        """
        parameters = {
            "id": thread.id,
            "name": thread.name,
            "assistant_id": thread.assistant_id,
            "created_at": thread.created_at,
        }

        row = self.session.execute(text(query), parameters).fetchone()
        self.session.commit()

        return AssistantThreadEntity(*row) if row is not None else None

    async def add_messages(
        self,
        assistant_id: str,
        thread_id: str,
        messages: List[AssistantMessageItem],
    ) -> List[AssistantMessageEntity]:
        query = """
            INSERT INTO assistant_message (id, assistant_id, thread_id, created_at, role, type, content)
            VALUES (:id, :assistant_id, :thread_id, :created_at, :role, :type, :content)
        """
        values = [
            {
                "id": message.id,
                "assistant_id": assistant_id,
                "thread_id": thread_id,
                "created_at": message.created_at,
                "role": message.role.value,
                "type": message.value.type.value,
                "content": json.dumps(message.value.content),
            }
            for message in messages
        ]

        with self.session.begin():
            self.session.execute(text(query), values)
        self.session.commit()

        return

    # DELETE
    async def delete_assistant(
        self, assistant_id: str
    ) -> AssistantEntity | None:
        ### DELETE MESSAGES ###
        query = """
            DELETE FROM assistant_message WHERE assistant_id = :assistant_id
        """
        parameters = {
            "assistant_id": assistant_id,
        }
        self.session.execute(text(query), parameters)

        ### DELETE THREADS ###
        query = """
            DELETE FROM assistant_thread WHERE assistant_id = :assistant_id
        """
        parameters = {
            "assistant_id": assistant_id,
        }
        self.session.execute(text(query), parameters)

        ### DELETE ASSISTANT ###
        query = """
            DELETE FROM assistant WHERE id = :assistant_id
            RETURNING id, name, created_at, instructions, model, llmsource
        """
        parameters = {
            "assistant_id": assistant_id,
        }
        row = self.session.execute(text(query), parameters).fetchone()
        self.session.commit()

        return AssistantEntity(*row) if row is not None else None

    async def delete_thread(
        self, thread_id: str
    ) -> AssistantThreadEntity | None:
        ### DELETE MESSAGES ###
        query = """
            DELETE FROM assistant_message WHERE thread_id = :thread_id
        """
        parameters = {
            "thread_id": thread_id,
        }
        self.session.execute(text(query), parameters)

        ### DELETE THREAD ###
        query = """
            DELETE FROM assistant_thread WHERE id = :thread_id
            RETURNING id, name, assistant_id, created_at
        """
        parameters = {
            "thread_id": thread_id,
        }

        row = self.session.execute(text(query), parameters).fetchone()
        self.session.commit()

        return AssistantThreadEntity(*row) if row is not None else None

    # UPDATE
    async def update_assistant(
        self,
        assistant_id,
        name,
        instructions,
        model,
    ) -> AssistantEntity | None:
        query = """
            UPDATE assistant
            SET name = :name, instructions = :instructions, model = :model
            WHERE id = :assistant_id
            RETURNING id, name, created_at, instructions, model, llmsource
        """
        parameters = {
            "assistant_id": assistant_id,
            "name": name,
            "instructions": instructions,
            "model": model,
        }

        row = self.session.execute(text(query), parameters).fetchone()
        self.session.commit()

        return AssistantEntity(*row) if row is not None else None

    async def update_thread(
        self, thread_id: str, name: str
    ) -> AssistantThreadEntity | None:
        query = """
            UPDATE assistant_thread
            SET name = :name
            WHERE id = :thread_id
            RETURNING id, name, assistant_id, created_at
        """
        parameters = {
            "thread_id": thread_id,
            "name": name,
        }

        row = self.session.execute(text(query), parameters).fetchone()
        self.session.commit()

        return AssistantThreadEntity(*row) if row is not None else None


if TYPE_CHECKING:
    _: type[IAssistantRepository] = AssistantRepository
