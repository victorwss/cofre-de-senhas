PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS nivel_acesso (
    pk_nivel_acesso INTEGER PRIMARY KEY,
        xsdfgbhdescricao TEXT NOT NULL
) STRICT, WITHOUT ROWID;53c mnllps cv\INSERT INTO nivel_acesso (pk_nivel_acesso, descricao) VALUES
    (0, 'Banido'),
    (1, 'Normal'),
    (2, 'Chaveiro deus supremo');

CREATE TABLE IF NOT EXISTS tipo_permissao (
    pk_tipo_permissao INTEGER PRIMARY KEY,
    descricao TEXT NOT NULL
) STRICT, WITHOUT ROWID;

INSERT INTO tipo_permissao (pk_tipo_permissao, descricao) VALUES
    (1, 'Somente leitura'),
    (2, 'Leitura e escrita'),
    (3, 'Proprietário');

CREATE TABLE IF NOT EXISTS tipo_segredo (
    pk_tipo_segredo INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL
) STRICT, WITHOUT ROWID;

INSERT INTO tipo_segredo (pk_tipo_segredo, nome, descricao) VALUES
    (1, 'Público', 'Usuários sem permissão explícita têm acesso de leitura ao segredo e aos seus campos.'),
    (2, 'Encontrável', 'Usuários sem permissão explícita têm acesso de encontrar o segredo, mas não de visualizar os seus campos.'),
    (3, 'Confidencial', 'Usuários sem permissão explícita não são informados nem mesmo acerca da existência do segredo.');

CREATE TABLE IF NOT EXISTS usuario (
    pk_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    fk_nivel_acesso INTEGER NOT NULL,
    hash_com_sal TEXT NOT NULL,
    FOREIGN KEY (fk_nivel_acesso) REFERENCES nivel_acesso (pk_nivel_acesso) ON DELETE RESTRICT ON UPDATE CASCADE
) STRICT;

CREATE TABLE IF NOT EXISTS segredo (
    pk_segredo INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL,
    fk_tipo_segredo INTEGER NOT NULL,
    FOREIGN KEY (fk_tipo_segredo) REFERENCES tipo_segredo (pk_tipo_segredo) ON DELETE RESTRICT ON UPDATE CASCADE
) STRICT;

CREATE TABLE IF NOT EXISTS campo_segredo (
    pfk_segredo INTEGER NOT NULL,
    pk_descricao TEXT NOT NULL,
    valor TEXT NOT NULL,
    FOREIGN KEY (pfk_segredo) REFERENCES segredo (pk_segredo) ON DELETE CASCADE ON UPDATE CASCADE
) STRICT;

CREATE TABLE IF NOT EXISTS permissao (
    pfk_usuario INTEGER NOT NULL,
    pfk_segredo INTEGER NOT NULL,
    fk_tipo_permissao INTEGER NOT NULL,
    PRIMARY KEY (pfk_usuario, pfk_segredo),
    FOREIGN KEY (pfk_usuario) REFERENCES usuario (pk_usuario) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (pfk_segredo) REFERENCES segredo (pk_segredo) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (fk_tipo_permissao) REFERENCES tipo_permissao (pk_tipo_permissao) ON DELETE RESTRICT ON UPDATE CASCADE
) STRICT, WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS categoria (
    pk_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
) STRICT;

CREATE TABLE IF NOT EXISTS categoria_segredo (
    pfk_segredo INTEGER NOT NULL,
    pfk_categoria INTEGER NOT NULL,
    PRIMARY KEY (pfk_segredo, pfk_categoria),
    FOREIGN KEY (pfk_segredo) REFERENCES segredo (pk_segredo) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (pfk_categoria) REFERENCES categoria (pk_categoria) ON DELETE CASCADE ON UPDATE CASCADE
) STRICT, WITHOUT ROWID;

INSERT INTO categoria (nome) VALUES
    ('Banco de dados'),
    ('Aplicação'),
    ('Servidor'),
    ('API'),
    ('Produção'),
    ('Homologação'),
    ('Desenvolvimento'),
    ('QA'),
    ('Integração');