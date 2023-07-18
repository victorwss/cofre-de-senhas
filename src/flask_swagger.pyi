from flask import Flask
from typing import Any, Callable

def swagger( \
        app: Flask, \
        prefix: str | None = None, \
        process_doc: Callable[[str], str] = ..., \
        from_file_keyword: str | None = None, \
        template: dict[str, Any] | None = None, \
        base_path: str = "" \
        ) -> dict[str, Any]:
    ...