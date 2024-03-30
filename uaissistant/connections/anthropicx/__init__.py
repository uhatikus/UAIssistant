from anthropic import Anthropic
from environs import Env
from injector import Module, provider
from pydantic.dataclasses import dataclass


@dataclass
class AnthropicConfig:
    api_key: str


class AnthropicModule(Module):
    @provider
    def provide_anthropic_config(self, env: Env) -> AnthropicConfig:
        return AnthropicConfig(
            api_key=env.str("ANTHROPIC_API_KEY"),
        )

    @provider
    def provide_anthropic(self, conf: AnthropicConfig) -> Anthropic:
        return Anthropic(api_key=conf.api_key)
