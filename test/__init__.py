def prepare_imports() -> None:
    import os
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

prepare_imports()