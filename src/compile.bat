python -m mypy --strict --install-types ^
    .\validator.py ^
    .\decorators\__init__.py ^
    .\decorators\for_all.py ^
    .\decorators\tracer.py ^
    .\connection\__init__.py ^
    .\connection\conn.py ^
    .\connection\mysqlconn.py ^
    .\connection\mariadbconn.py ^
    .\mariadb\__init__.pyi ^
    .\mariadb\connections.pyi ^
    .\mariadb\cursors.pyi ^
    .\mariadb\constants\__init__.pyi ^
    .\mariadb\constants\FIELD_FLAG.pyi ^
    .\mariadb\constants\FIELD_TYPE.pyi ^
    .\connection\sqlite3conn.py ^
    .\cofre_de_senhas\__init__.py ^
    .\cofre_de_senhas\model.py ^
    .\cofre_de_senhas\dao.py ^
    .\cofre_de_senhas\service.py ^
    .\cofre_de_senhas\dao_impl.py ^
    .\cofre_de_senhas\service_impl.py