import typing as t
from sanic import Sanic, __version__
from sanic.exceptions import SanicException
from sanic.log import logger

from .config import add_fallback_config, Config
from .extensions.base import Extension
from .extensions.injection.extension import InjectionExtension
from .extensions.injection.registry import InjectionRegistry
from .extensions.openapi.extension import OpenAPIExtension
from .extensions.http.extension import HTTPExtension

MIN_SUPPORT = (21, 3, 2)

class Extend:

    def __init__(
            self,
            app: Sanic,
            *,
            extensions: t.Optional[t.List[t.Type[Extension]]] = None,
            built_in_extensions: bool = True,
            config: t.Optional[t.Union[Config, t.Dict[str, t.Any]]] = None,
            **kwargs
    ):
        if not isinstance(app, Sanic):
            raise SanicException(
                f"Cannot apply SanicExt to {app.__class__.__name__}"
            )
        sanic_version = tuple(map(int, __version__.split(".")))
        if MIN_SUPPORT > sanic_version:
            min_version = ".".join(map(str, MIN_SUPPORT))
            raise SanicException(
                f"SanicExt only works with Sanic v{min_version} and above. "
                f"It looks like you are running {__version__}"
            )
        self.app = app
        self._injection_registry: t.Optional[InjectionRegistry] = None
        app.ctx.ext = self

        if not isinstance(config, Config):
            config = Config.from_dict(config or {})
        self.config = add_fallback_config(app, config, **kwargs)

        if not extensions:
            extensions = []

        if built_in_extensions:
            extensions.extend(
                [
                    InjectionExtension,
                    OpenAPIExtension,
                    HTTPExtension
                ]
            )
        init_logs = ["Sanic Extensions:"]
        for extclass in extensions[::-1]:
            extension = extclass(app, self.config)
            extension._startup(self)
            init_logs.append(f"  > {extension.name} {extension.labels()}")

        list(map(logger.info, init_logs))

    def injection(self, type: t.Type, constructor: t.Optional[t.Callable[..., t.Any]] = None):
        if not self._injection_registry:
            raise SanicException("Injection extension not able")
        self._injection_registry.register(type, constructor)
