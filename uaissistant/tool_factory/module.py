from injector import Module, provider
from sqlalchemy.orm import Session
from uaissistant.tool_factory.repository import (
    IToolFactoryRepository,
    ToolFactoryRepository,
)
from uaissistant.tool_factory.service import (
    IToolFactoryService,
    ToolFactoryService,
)


class ToolFactoryModule(Module):
    @provider
    def provide_tool_factory_service(
        self, tfr: IToolFactoryRepository
    ) -> IToolFactoryService:
        return ToolFactoryService(tfr=tfr)

    @provider
    def provide_tool_factory_repository(
        self, session: Session
    ) -> IToolFactoryRepository:
        return ToolFactoryRepository(session=session)
