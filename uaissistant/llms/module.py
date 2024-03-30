from typing import Dict
from uaissistant.llms.anthropic.repository import IAnthropicRepository
from uaissistant.llms.llm import LLM
from uaissistant.llms.openai.openaillm import OpenAILLM
from uaissistant.tool_factory.service import IToolFactoryService
from injector import Module, multiprovider
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
    ) -> Dict[str, LLM]:
        return {
            "openai": OpenAILLM(
                client=openai_client, tool_factory=tool_factory
            ),
            "anthropic": AnthropicLLM(
                client=anthropic_client,
                tool_factory=tool_factory,
                anthropic_repository=anthropic_repository,
            ),
        }
