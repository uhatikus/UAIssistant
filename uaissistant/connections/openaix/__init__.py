from environs import Env
from injector import Module, provider
from openai import OpenAI
from pydantic.dataclasses import dataclass


@dataclass
class OpenAiConfig:
    api_key: str


class OpenAiModule(Module):
    @provider
    def provide_openai_config(self, env: Env) -> OpenAiConfig:
        return OpenAiConfig(
            api_key=env.str("OPENAI_API_KEY"),
        )

    @provider
    def provide_openai(self, conf: OpenAiConfig) -> OpenAI:
        return OpenAI(api_key=conf.api_key)
