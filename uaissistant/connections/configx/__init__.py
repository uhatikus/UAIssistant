from environs import Env
from injector import Module, provider

class ConfigModule(Module):
    @provider
    def provide_env(self) -> Env:
        env = Env()
        env.read_env()
        return env
