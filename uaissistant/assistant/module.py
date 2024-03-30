from typing import Dict
from uaissistant.assistant.repository import (
    AssistantRepository,
    IAssistantRepository,
)
from uaissistant.assistant.service import AssistantService, IAssistantService
from uaissistant.llms.llm import LLM
from injector import Module, provider
from sqlalchemy.orm import Session


class AssistantModule(Module):
    @provider
    def provide_assistant_service(
        self, ar: IAssistantRepository, llms: Dict[str, LLM]
    ) -> IAssistantService:
        return AssistantService(ar=ar, llms=llms)

    @provider
    def provide_assistant_repository(
        self, session: Session
    ) -> IAssistantRepository:
        return AssistantRepository(session=session)
