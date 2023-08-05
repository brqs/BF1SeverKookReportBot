import yaml

from abc import ABC
from pathlib import Path
from typing import List, Type
from creart import add_creator, AbstractCreator, CreateTargetInfo, exists_module
from pydantic import BaseModel
from utils.Singleton import singleton


class GlobalConfig(BaseModel):
    db_link: str = "sqlite+aiosqlite:///data.db"
    functions: dict = {
        "bf1": {
            "default_account": int,
            "apikey": str
        },
        "image_search": {
            "saucenao_key": str
        },
        "steamdb_cookie": str,
    }
@singleton
class ConfigLoader:
    def __init__(self):
        with open(Path().cwd() / "config" / "config.yaml", "r", encoding="utf-8") as f:
            self.config_data = yaml.safe_load(f.read())

    def load_config(self) -> GlobalConfig:
        return GlobalConfig(**self.config_data)


class ConfigClassCreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("core.config", "GlobalConfig"),)

    @staticmethod
    def available() -> bool:
        return exists_module("core.config")

    @staticmethod
    def create(create_type: Type[GlobalConfig]) -> GlobalConfig:
        config_loader = ConfigLoader()
        config = config_loader.load_config()
        return config


add_creator(ConfigClassCreator)
