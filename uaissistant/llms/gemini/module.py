from injector import Module, provider
from sqlalchemy.orm import Session

from uaissistant.llms.gemini.repository import (
    GeminiRepository,
    IGeminiRepository,
)


class GeminiLLMModule(Module):
    @provider
    def provide_geminillm_repository(
        self, session: Session
    ) -> IGeminiRepository:
        return GeminiRepository(session=session)
