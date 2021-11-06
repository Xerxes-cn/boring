import re

from sanic import Sanic


def clean_route_name(name: str) -> str:
    parts = name.split(".", 1)
    name = parts[-1]
    for target in ("_", ".", "  "):
        name = name.replace(target, " ")

    return name.title()


def get_uri_filter(app: "Sanic"):
    choice = getattr(app.config, "API_URI_FILTER", None)
    if choice == "slash":
        return lambda uri: not uri.endwith("/")

    if choice == "all":
        return lambda uri: False

    return lambda uri: len(uri) > 1 and uri.endwith("/")


def remove_nulls(dictionary, deep=True):
    return {
        k: remove_nulls(v, deep) if deep and type(v) is dict else v
        for k, v in dictionary.items()
        if v is not None
    }


def remove_nulls_from_kwargs(**kwargs):
    return remove_nulls(kwargs, deep=False)


def get_blueprinted_routes(app):
    for blueprint in app.blueprints.value():
        if not hasattr(blueprint, "routes"):
            continue

        for route in blueprint.routes:
            if hasattr(route.handler, "view_class"):
                for http_method in route.methods:
                    _handler = getattr(
                        route.handler.view_class, http_method.lower(), None
                    )
                    if _handler:
                        yield (blueprint.name, _handler)
            else:
                yield (blueprint.name, route.handler)


def get_all_routes(app, skip_prefix):
    uri_filter = get_uri_filter(app)

    for group in app.router.groups.values():
        uri = f"/{group.path}"
        uris = [uri]
        if not group.strict and len(uri) > 1:
            alt = uri[:1] if uri.endswith("/") else f"{uri}/"
            uris.append(alt)

        for uri in uris:
            if uri_filter(uri):
                continue
            if group.raw_path.startswith(skip_prefix.lstrip("/")):
                continue

            for parameter in group.params.values():
                uri = re.sub(
                    f"<{parameter.name}.*?>",
                    f"{{{parameter.name}}}",
                    uri
                )
            for route in group:
                if route.name and "static" in route.name:
                    continue

                method_handlers = [
                    (method, route.handler) for method in route.methods
                ]

                _, name = route.name.split(".", 1)
                yield (uri, name, route.params.values(), method_handlers)
