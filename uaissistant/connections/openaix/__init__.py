from environs import Env
from injector import Module, provider
from openai import OpenAI
from pydantic.dataclasses import dataclass


@dataclass
class OpenAiConfig:
    api_key: str
    org_id: str


class OpenAiModule(Module):
    @provider
    def provide_openai_config(self, env: Env) -> OpenAiConfig:
        return OpenAiConfig(
            api_key=env.str("OPENAI_API_KEY"),
            org_id=env.str("OPENAI_ORG_ID"),
        )

    @provider
    def provide_openai(self, conf: OpenAiConfig) -> OpenAI:
        return OpenAI(api_key=conf.api_key, organization=conf.org_id)
