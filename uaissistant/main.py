from uaissistant.assistant import AssistantModule
from uaissistant.connections import (
    AnthropicModule,
    ConfigModule,
    DbModule,
    OpenAiModule,
)
from uaissistant.llms import LlmsModule
from uaissistant.llms.anthropic.module import AnthropicLLMModule
from uaissistant.llms.gemini.module import GeminiLLMModule
from uaissistant.tool_factory import ToolFactoryModule
from injector import Injector
from fastapi import FastAPI
from fastapi_injector import (
    InjectorMiddleware,
    RequestScopeOptions,
    attach_injector,
)
from uaissistant.routes import assistant
from fastapi.middleware.cors import CORSMiddleware

injector = Injector(
    [
        # assistant module
        AssistantModule(),
        # toolfactory module
        ToolFactoryModule(),
        # connections
        ConfigModule(),
        DbModule(),
        OpenAiModule(),
        AnthropicModule(),
        # llm modules
        LlmsModule(),
        AnthropicLLMModule(),
        GeminiLLMModule(),
    ]
)
app = FastAPI(root_path="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(InjectorMiddleware, injector=injector)
app.include_router(assistant.router)
attach_injector(app, injector, options=RequestScopeOptions(enable_cleanup=True))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
