from inspect import isawaitable

from sanic import Sanic


def app_injection(app: Sanic, injection_registry: InjectionRegistry):
    signature_registry = _setup_signature_registry(app, injection_registry)

    @app.signal("http.routing.after")
    async def inject_kwargs(request, route, kwargs, **_):
        nonlocal signature_registry

        injections = signature_registry[route.name]
        injected_args = {
            name: await _do_cast(_type, constructor, request, **kwargs)
            for name, (_type, constructor) in injections.items()
        }
        request.match_info.update(injected_args)


async def _do_cast(_type, constructor, request, **kwargs):
    cast = constructor if constructor else _type
    args = [request] if constructor else []
    retval = cast(*args, **kwargs)
    if isawaitable(retval):
        retval = await retval
    return retval
