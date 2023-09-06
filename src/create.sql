PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS enum_nivel_acesso (
    pk_nivel_acesso INTEGER NOT NULL PRIMARY KEY,
    descricao       TEXT    NOT NULL UNIQUE
) STRICT, WITHOUT ROWID;

INSERT INTO enum_nivel_acesso (pk_nivel_acesso, descricao) VALUES
    (0, 'Banido'               ),
    (1, 'Normal'               ),
    (2, 'Chaveiro deus supremo');

CREATE TABLE IF NOT EXISTS enum_tipo_permissao (
    pk_tipo_permissao INTEGER NOT NULL PRIMARY KEY,
    descricao         TEXT    NOT NULL UNIQUE
) STRICT, WITHOUT ROWID;

INSERT INTO enum_tipo_permissao (pk_tipo_permissao, descricao) VALUES
    (1, 'Somente leitura'  ),
    (2, 'Leitura e escrita'),
    (3, 'Proprietário'     );

CREATE TABLE IF NOT EXISTS enum_tipo_segredo (
    pk_tipo_segredo INTEGER NOT NULL PRIMARY KEY,
    nome            TEXT    NOT NULL UNIQUE,
    descricao       TEXT    NOT NULL
) STRICT, WITHOUT ROWID;

INSERT INTO enum_tipo_segredo (pk_tipo_segredo, nome, descricao) VALUES
    (1, 'Público'     , 'Usuários sem permissão explícita têm acesso de leitura ao segredo e aos seus campos.'                     ),
    (2, 'Encontrável' , 'Usuários sem permissão explícita têm acesso de encontrar o segredo, mas não de visualizar os seus campos.'),
    (3, 'Confidencial', 'Usuários sem permissão explícita não são informados nem mesmo acerca da existência do segredo.'           );

CREATE TABLE IF NOT EXISTS categoria (
    pk_categoria INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    nome         TEXT    NOT NULL UNIQUE      CHECK (LENGTH(nome) <= 50)
) STRICT;

INSERT INTO categoria (pk_categoria, nome) VALUES
    (1, 'Banco de dados' ),
    (2, 'Aplicação'      ),
    (3, 'Servidor'       ),
    (4, 'API'            ),
    (5, 'Produção'       ),
    (6, 'Homologação'    ),
    (7, 'Desenvolvimento'),
    (8, 'QA'             ),
    (9, 'Integração'     );
UPDATE sqlite_sequence SET seq = 9 WHERE name = 'categoria';

CREATE TABLE IF NOT EXISTS usuario (
    pk_usuario      INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    login           TEXT    NOT NULL UNIQUE      CHECK (LENGTH(login) >= 4 AND LENGTH(login) <= 50),
    fk_nivel_acesso INTEGER NOT NULL,
    hash_com_sal    TEXT    NOT NULL,
    FOREIGN KEY (fk_nivel_acesso) REFERENCES enum_nivel_acesso (pk_nivel_acesso) ON DELETE RESTRICT ON UPDATE CASCADE
) STRICT;

CREATE TABLE IF NOT EXISTS segredo (
    pk_segredo      INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    nome            TEXT    NOT NULL             CHECK (LENGTH(nome) >= 4 AND LENGTH(nome     ) <=  50),
    descricao       TEXT    NOT NULL             CHECK (                      LENGTH(descricao) <= 500),
    fk_tipo_segredo INTEGER NOT NULL,
    FOREIGN KEY (fk_tipo_segredo) REFERENCES enum_tipo_segredo (pk_tipo_segredo) ON DELETE RESTRICT ON UPDATE CASCADE
) STRICT;

CREATE TABLE IF NOT EXISTS campo_segredo (
    pfk_segredo INTEGER NOT NULL,
    pk_chave    TEXT    NOT NULL CHECK (LENGTH(pk_chave) >= 0 AND LENGTH(pk_chave) <=  500),
    valor       TEXT    NOT NULL CHECK (                          LENGTH(valor   ) <= 5000),
    PRIMARY KEY (pfk_segredo, pk_chave),
    FOREIGN KEY (pfk_segredo) REFERENCES segredo (pk_segredo) ON DELETE CASCADE ON UPDATE CASCADE
) STRICT, WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS categoria_segredo (
    pfk_segredo   INTEGER NOT NULL,
    pfk_categoria INTEGER NOT NULL,
    PRIMARY KEY (pfk_segredo, pfk_categoria),
    FOREIGN KEY (pfk_segredo  ) REFERENCES segredo   (pk_segredo  ) ON DELETE CASCADE  ON UPDATE CASCADE,
    FOREIGN KEY (pfk_categoria) REFERENCES categoria (pk_categoria) ON DELETE RESTRICT ON UPDATE CASCADE
) STRICT, WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS permissao (
    pfk_usuario       INTEGER NOT NULL,
    pfk_segredo       INTEGER NOT NULL,
    fk_tipo_permissao INTEGER NOT NULL,
    PRIMARY KEY (pfk_usuario, pfk_segredo),
    FOREIGN KEY (pfk_usuario      ) REFERENCES usuario             (pk_usuario       ) ON DELETE CASCADE  ON UPDATE CASCADE,
    FOREIGN KEY (pfk_segredo      ) REFERENCES segredo             (pk_segredo       ) ON DELETE CASCADE  ON UPDATE CASCADE,
    FOREIGN KEY (fk_tipo_permissao) REFERENCES enum_tipo_permissao (pk_tipo_permissao) ON DELETE RESTRICT ON UPDATE CASCADE
) STRICT, WITHOUT ROWID;

INSERT INTO segredo (pk_segredo, nome, descricao, fk_tipo_segredo) VALUES (-1, 'Cofre de senhas', 'Segredos acerca do guardador de segredos.', 2);
INSERT INTO campo_segredo (pfk_segredo, pk_chave, valor) VALUES (-1, 'Chave da sessão', HEX(RANDOMBLOB(256)));
INSERT INTO categoria_segredo (pfk_segredo, pfk_categoria) VALUES (-1, 2);