from cofre_de_senhas.controller import servir
from connection.load import DatabaseConfig

PORTA: int = 5000

if __name__ == "__main__":
    servir(PORTA, DatabaseConfig.from_file("cofre.json"))

    # Workaround for bug https://github.com/python/cpython/issues/115533 and https://github.com/python/cpython/issues/113964
    # See https://github.com/python/cpython/issues/115533#issuecomment-1959143451
    import threading
    for thread in threading.enumerate():
        if thread.daemon or thread is threading.current_thread():
            continue
        thread.join()
