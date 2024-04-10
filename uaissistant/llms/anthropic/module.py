from injector import Module, provider
from sqlalchemy.orm import Session

from uaissistant.llms.anthropic.repository import (
    AnthropicRepository,
    IAnthropicRepository,
)


class AnthropicLLMModule(Module):
    @provider
    def provide_anthropicllm_repository(
        self, session: Session
    ) -> IAnthropicRepository:
        return AnthropicRepository(session=session)
