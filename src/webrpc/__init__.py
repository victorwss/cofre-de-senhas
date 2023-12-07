from .webrpc import ( \
    WebMethod, \
    Converter, \
    WebParam, \
    WebSuite,
    from_body_typed
)

__all__: tuple[str, ...] = ( \
    "WebMethod", \
    "Converter", \
    "WebParam", \
    "WebSuite", \
    "from_body_typed" \
)