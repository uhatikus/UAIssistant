from injector import Module, provider
from sqlalchemy.orm import Session

from uaissistant.llms.anthropic.repository import (
    AnthropicRepository,
    IAnthropicRepository,
)


class ToolFactoryModule(Module):
    @provider
    def provide_anthropic_repository(
        self, session: Session
    ) -> IAnthropicRepository:
        return AnthropicRepository(session=session)
