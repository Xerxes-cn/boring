from abc import ABC, abstractmethod
from typing import Dict, Type

from sanic import Sanic
from sanic.config import Config
from sanic.exceptions import SanicException

from ..exceptions import InitError

class NoDuplicationDict(dict):
    def __setitem__(self, key, value):
        if key in self:
            raise KeyError(f"Duplicate key: {key}")
        return super().__setitem__(key, value)


class Extension(ABC):
    _name_register: Dict[str, Type["Extension"]] = NoDuplicationDict()
    _singleton = None
    name: str

    def __new__(cls, *args, **kwargs):
        if cls._singleton is None:
            cls._singleton = super().__new__(cls)
            cls._singleton._started = False
        return cls._singleton

    def __init_subclass__(cls):
        if not getattr(cls, "name", None) or not cls.name.isalpha():
            raise InitError(
                "Extensions must be named, and may only contain alphabetic characters"
            )
        if cls.name in cls._name_register:
            raise InitError(f"Extension '{cls.name}' already exists")

        cls._name_register[cls.name] = cls

    def __init__(self, app: Sanic, config: Config) -> None:
        self.app = app
        self.config = config

    def _startup(self, bootstrap):
        if self._started:
            raise SanicException(
                f"Extension already started. Cannot start Extension: {self.name} multiple times."
            )
        self.startup(bootstrap)
        self._started = True

    @abstractmethod
    def startup(self, bootstrap) -> None:
        ...

    def label(self):
        return ""
