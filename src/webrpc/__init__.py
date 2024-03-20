from .webrpc import (
    WebMethod,
    WebParam,
    WebSuite,
    from_body_typed,
    from_path,
    from_path_int,
    from_path_float,
    identity,
    parse_int,
    parse_float
)

__all__: tuple[str, ...] = (
    "WebMethod",
    "WebParam",
    "WebSuite",
    "from_body_typed",
    "from_path",
    "from_path_int",
    "from_path_float",
    "identity",
    "parse_int",
    "parse_float"
)
