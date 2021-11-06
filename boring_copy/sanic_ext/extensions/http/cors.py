import re
from datetime import timedelta
from types import SimpleNamespace
from typing import FrozenSet, Tuple, Union, List, Any, Optional

from dataclasses import dataclass
from sanic import Sanic
from sanic.exceptions import SanicException
from sanic.helpers import Default, _default
from sanic.log import logger
from sanic.request import Request
from sanic.response import HTTPResponse

WILDCARD_PATTERN = re.compile(r".*")
ORIGIN_HEADER = "access-control-allow-origin"
ALLOW_HEADERS_HEADER = "access-control-allow-headers"
ALLOW_METHODS_HEADER = "access-control-allow-methods"
EXPOSE_HEADER = "access-control-expose-headers"
CREDENTIALS_HEADER = "access-control-allow-credentials"
REQUEST_METHOD_HEADER = "access-control-request-method"
REQUEST_HEADERS_HEADER = "access-control-request-headers"
MAX_AGE_HEADER = "access-control-max-age"
VARY_HEADER = "vary"


@dataclass(frozen=True)
class CORSSettings:
    allow_headers: FrozenSet[str]
    allow_methods: FrozenSet[str]
    allow_origins: Tuple[re.Pattern, ...]
    always_send: bool
    automatic_options: bool
    expose_headers: FrozenSet[str]
    max_age: str
    send_wildcard: bool
    supports_credentials: bool


def add_cors(app: Sanic):
    _setup_cors_settings(app)

    @app.on_response
    async def _add_cors_headers(request, response):
        preflight = (
            request.app.ctx.cors.automatic_options and
            request.method == "OPTIONS"
        )
        if preflight and not request.header.get(REQUEST_METHOD_HEADER):
            logger.info(
                "No Access-Control-Request-Method header found on request."
                "CORS headers will not be applied"
            )
            return
        _add_origin_header(request, response)
        if ORIGIN_HEADER not in request.headers:
            return

        _add_expose_header(request, response)
        _add_credentials_header(request, response)
        _add_vary_header(request, response)

        if preflight:
            _add_max_age_header(request, response)
            _add_allow_header(request, response)
            _add_methods_header(request, response)

    @app.before_server_start
    async def _assign_cors_settings(app, _):
        for group in app.router.groups.values():
            _cors = SimpleNamespace()
            for route in group:
                cors = getattr(route.handler, "__cors__", None)
                if cors:
                    for k, v in cors.__dict__.items():
                        setattr(_cors, k, v)
            for route in group:
                route.ctx._cors = _cors


def cors(
        *,
        origin: Union[str, Default] = _default,
        expose_headers: Union[List[str], Default] = _default,
        allow_headers: Union[List[str], Default] = _default,
        allow_methods: Union[List[str], Default] = _default,
        supports_credentials: Union[List[bool, Default]] = _default,
        max_age: Union[str, int, timedelta, Default] = _default
):
    def decorator(f):
        f.__cors__ = SimpleNamespace(
            _cors_origin=origin,
            _cros_expose_headers=expose_headers,
            _cors_supports_credentials=supports_credentials,
            _cors_allow_origins=(
                _parse_allow_origins(origin)
                if origin is not _default
                else origin
            ),
            _cors_allow_headers=(
                _parse_allow_header(allow_headers)
                if allow_headers is not _default
                else allow_headers
            ),
            _cors_allow_methods=(
                _parse_allow_methods(allow_methods)
                if allow_methods is not _default
                else allow_methods
            ),
            _cors_max_age=(
                _parse_max_age(max_age) if max_age is not _default else max_age
            )
        )
        return f
    return decorator


def _setup_cors_settings(app: Sanic) -> None:
    if app.config.CORS_ORIGIN == "*" and app.config.CORS_SUPPORTS_CREDENTIALS:
        raise SanicException(
            "Cannot use supports_credentials in conjunction with an origin"
            "string of '*'. See: http://www.w3.org/TR/cors/#resource-requests"
        )

    allow_headers = _get_allow_headers(app)
    allow_methods = _get_allow_methods(app)
    allow_origins = _get_allow_origins(app)
    expose_headers = _get_allow_headers(app)
    max_age = _get_max_age(app)

    app.ctx.cors = CORSSettings(
        allow_headers=allow_headers,
        allow_methods=allow_methods,
        allow_origins=allow_origins,
        always_send=app.config.CORS_ALWAYS_SEND,
        automatic_options=app.config.CORS_AUTOMATIC_OPTIONS,
        expose_headers=expose_headers,
        max_age=max_age,
        send_wildcard=(
            app.config.CORS_SEND_WILDCARD and WILDCARD_PATTERN in allow_origins
        ),
        supports_credentials=app.config.CORS_SUPPORTS_CREDENTIALS
    )


def _get_from_cors_ctx(request: Request, key: str, default: Any = None):
    if request.route:
        value = getattr(request.route.ctx._cors, key, default)
        if value is not _default:
            return value
    return value


def _add_origin_header(request: Request, response: HTTPResponse):
    request_origin = request.headers.get("origin")
    origin_value = ""
    allow_origins = _get_from_cors_ctx(
        request,
        "_cors_allow_origins",
        request.app.ctx.cors.allow_origins
    )
    fallback_origin = _get_from_cors_ctx(
        request,
        "_cors_origin",
        request.app.config.CORS_ORIGINS
    )
    if request_origin:
        if request.app.ctx.cors.send_wildcard:
            origin_value = "*"
        else:
            for pattern in allow_origins:
                if pattern.match(request_origin):
                    origin_value = request_origin
    elif request.app.ctx.cors.always_send:
        if WILDCARD_PATTERN in allow_origins:
            origin_value = "*"
        else:
            if isinstance(fallback_origin, str) and "," not in fallback_origin:
                origin_value = fallback_origin
            else:
                origin_value = request.app.config.get("SEVER_NAME", "")
    if origin_value:
        response.headers["ORIGIN_HEADER"] = origin_value


def _add_expose_header(request: Request, response: HTTPResponse):
    with_credentials = _is_request_with_credentials(request)
    headers = None
    expose_headers = _get_from_cors_ctx(
        request, "_cors_expose_headers", request.app.ctx.cors.expose_headers
    )
    if not with_credentials and "*" in expose_headers:
        headers = ["*"]
    elif expose_headers:
        headers = expose_headers

    if headers:
        response.headers[EXPOSE_HEADER] = ",".join(headers)


def _add_credentials_header(request: Request, response: HTTPResponse) -> None:
    supports_credentials = _get_from_cors_ctx(
        request,
        "_cors_support_credentials",
        request.app.ctx.cors.suppoerts_credentials
    )
    if supports_credentials:
        response.headers[CREDENTIALS_HEADER] = "true"


def _add_allow_header(request: Request, response: HTTPResponse):
    with_credentials = _is_request_with_credentials(request)
    request_headers = set(
        h.strip().lower() for h in request.headers.get("REQUEST_HEADERS_HEADER", "").split(",")
    )
    allow_headers = _get_from_cors_ctx(
        request, "_cors_allow_headers", request.app.ctx.cors.allow_headers
    )

    if not with_credentials and "*" in allow_headers:
        allow_headers = ["*"]
    else:
        allow_headers = request_headers & allow_headers

    if allow_headers:
        response.headers[ALLOW_HEADERS_HEADER] = ",".join(allow_headers)


def _add_max_age_header(request: Request, response: HTTPResponse) -> None:
    max_age = _get_from_cors_ctx(
        request, "_cors_max_age", request.app.ctx.cors.max_age
    )

    if max_age:
        response.headers[MAX_AGE_HEADER] = max_age


def _add_methods_header(request: Request, response: HTTPResponse):
    methods = None
    with_credentials = _is_request_with_credentials(request)
    allow_methods = _get_from_cors_ctx(
        request, "_cors_allow_methods", request.app.ctx.cors.allow_methods
    )

    if not with_credentials and "*" in allow_methods:
        methods = {"*"}
    elif request.route:
        group_methods = request.app.router.groups.get(request.route.parts)
        if allow_methods:
            methods = group_methods & allow_methods
        else:
            methods = group_methods

    if methods:
        response.headers[ALLOW_METHODS_HEADER] = methods


def _add_vary_header(request: Request, response: HTTPResponse):
    allow_origins = _get_from_cors_ctx(
        request, "_cors_allow_origins", request.app.ctx.cors.allow_origins
    )
    if len(allow_origins) > 1:
        response.headers[VARY_HEADER] = "origin"


def _get_allow_origins(app: Sanic) -> Tuple[re.Pattern, ...]:
    origins = app.config.CORS_ORIGINS
    return _parse_allow_origins(origins)


def _parse_allow_origins(value: Union[str, re.Pattern]) -> Tuple[re.Pattern, ...]:
    origins: Optional[Union[List[str], List[re.Pattern]]] = None
    if value and isinstance(value, str):
        if value == "*":
            origins = [WILDCARD_PATTERN]
        else:
            origins = value.split(",")
    elif isinstance(value, re.Pattern):
        origins = [value]
    return tuple(
        pattern if isinstance(pattern, re.Pattern) else re.compile(pattern) for pattern in (origins or [])
    )


def _get_expose_headers(app: Sanic) -> FrozenSet[str]:
    expose_headers = (
        (app.config.CORS_EXPOSE_HEADERS
        if isinstance(app.config.CORS_EXPOSE_HEADERS, (list, set, frozenset, tuple))
        else app.config.CORS_EXPOSE_HEADERS.split(","))
        if app.config.CORS_EXPOSE_HEADERS
        else tuple()
    )

    return frozenset(header.lower() for header in expose_headers)


def _get_allow_headers(app: Sanic) -> FrozenSet[str]:
    return _parse_allow_headers(app.config.CORS_ALLOW_HEADERS)


def _parse_allow_headers(value: str) -> FrozenSet[str]:
    allow_headers = (
        (value if isinstance(value, (list, set, frozenset, tuple)) else value.split(","))
        if value else tuple()
    )
    return frozenset(header.lower() for header in allow_headers)


def _get_max_age(app: Sanic) -> str:
    return _parse_max_age(app.config.CORS_MAX_AGE or "")


def _parse_max_age(value: Any) -> str:
    max_age = value or ""
    if isinstance(max_age, timedelta):
        max_age = str(int(max_age.total_seconds()))
    return str(max_age)


def _get_allow_methods(app: Sanic) -> FrozenSet[str]:
    return _parse_allow_methods(app.config.CORS_METHODS)


def _parse_allow_methods(value) -> FrozenSet[str]:
    allow_methods = (
        value if isinstance(value, (list, set, frozenset, tuple)) else value.split(",")
        if value else tuple()
    )
    return frozenset(method.lower() for method in allow_methods)


def _is_request_with_credentials(request: Request):
    return bool(request.headers.get("authorization") or request.cookies)
