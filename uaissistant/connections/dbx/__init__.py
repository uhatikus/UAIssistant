from environs import Env
from fastapi_injector import request_scope
from injector import Module, provider
from pydantic.dataclasses import dataclass
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


@dataclass
class DbConfig:
    host: str
    port: int
    user: str
    password: str
    database: str
    sslmode: str

    def connection_string(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?sslmode={self.sslmode}"


class DbModule(Module):
    @provider
    def provide_db_config(self, env: Env) -> DbConfig:
        return DbConfig(
            host=env.str("DB_HOST"),
            port=env.int("DB_PORT", default=5432),
            user=env.str("DB_USER"),
            password=env.str("DB_PASSWORD"),
            database=env.str("DB_DATABASE"),
            sslmode=env.str("DB_SSLMODE", default="require"),
        )

    @provider
    def provide_engine(self, conf: DbConfig) -> Engine:
        return create_engine(conf.connection_string())

    @provider
    def provide_sessionmaker(self, engine: Engine) -> sessionmaker[Session]:
        return sessionmaker(autocommit=False, autoflush=False, bind=engine)

    @provider
    @request_scope
    def provide_session(self, Session: sessionmaker[Session]) -> Session:
        return Session()
