from typing import Dict

from environs import Env
from uaissistant.assistant.schemas import LLMSource
from uaissistant.llms.anthropic.repository import (
    AnthropicRepository,
    IAnthropicRepository,
)
from uaissistant.llms.gemini.geminillm import GeminiLLM
from uaissistant.llms.gemini.repository import IGeminiRepository
from uaissistant.llms.llm import LLM
from uaissistant.llms.openai.openaillm import OpenAILLM
from uaissistant.tool_factory.service import IToolFactoryService
from injector import Module, multiprovider, provider
from sqlalchemy.orm import Session
from openai import Client

from anthropic import Anthropic
from uaissistant.llms.anthropic.anthropicllm import AnthropicLLM


class LlmsModule(Module):
    @multiprovider
    def provide_llms(
        self,
        openai_client: Client,
        anthropic_client: Anthropic,
        tool_factory: IToolFactoryService,
        anthropic_repository: IAnthropicRepository,
        gemini_repository: IGeminiRepository,
        env: Env,
    ) -> Dict[str, LLM]:
        return {
            LLMSource.OpenAI: OpenAILLM(
                client=openai_client, tool_factory=tool_factory
            ),
            LLMSource.Anthropic: AnthropicLLM(
                client=anthropic_client,
                tool_factory=tool_factory,
                anthropic_repository=anthropic_repository,
            ),
            LLMSource.Gemini: GeminiLLM(
                env=env,
                tool_factory=tool_factory,
                gemini_repository=gemini_repository,
            ),
        }

    @provider
    def provide_anthropic_repository(
        self, session: Session
    ) -> IAnthropicRepository:
        return AnthropicRepository(session=session)
