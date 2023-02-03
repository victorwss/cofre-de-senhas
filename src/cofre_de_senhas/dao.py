class DAO:

    def sql_criar_bd():
        with open("create.sql", "r") as f:
            return f.read()

    def sql_criar_usuario():
        return "INSERT INTO usuario(login, hash_com_sal) VALUES (?, ?)"

    def sql_localizar_usuario():
        return "SELECT FROM usuario WHERE login = ?"

    def sql_login():
        return "SELECT FROM usuario WHERE login = ? AND hash_com_sal = ?"

    def sql_trocar_senha():
        return "UPDATE usuario SET hash_com_sal = ? WHERE login = ?"