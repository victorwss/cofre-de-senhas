DROP TABLE IF EXISTS permissao;
DROP TABLE IF EXISTS categoria_segredo;
DROP TABLE IF EXISTS campo_segredo;
DROP TABLE IF EXISTS segredo;
DROP TABLE IF EXISTS categoria;
DROP TABLE IF EXISTS usuario;
DROP TABLE IF EXISTS enum_nivel_acesso;
DROP TABLE IF EXISTS enum_tipo_permissao;
DROP TABLE IF EXISTS enum_tipo_segredo;

-- DROP DATABASE IF EXISTS $$$$;
-- CREATE DATABASE $$$$ /*!40100 COLLATE 'utf8mb4_general_ci' */;
-- USE $$$$;

CREATE TABLE IF NOT EXISTS enum_nivel_acesso (
    pk_nivel_acesso INTEGER     NOT NULL PRIMARY KEY,
    descricao       VARCHAR(21) NOT NULL UNIQUE
) ENGINE = INNODB;

INSERT INTO enum_nivel_acesso (pk_nivel_acesso, descricao) VALUES
    (0, 'Banido'               ),
    (1, 'Normal'               ),
    (2, 'Chaveiro deus supremo');

CREATE TABLE IF NOT EXISTS enum_tipo_permissao (
    pk_tipo_permissao INTEGER     NOT NULL PRIMARY KEY,
    descricao         VARCHAR(17) NOT NULL UNIQUE
) ENGINE = INNODB;

INSERT INTO enum_tipo_permissao (pk_tipo_permissao, descricao) VALUES
    (1, 'Somente leitura'  ),
    (2, 'Leitura e escrita'),
    (3, 'Proprietário'     );

CREATE TABLE IF NOT EXISTS enum_tipo_segredo (
    pk_tipo_segredo INTEGER      NOT NULL PRIMARY KEY,
    nome            VARCHAR( 22) NOT NULL UNIQUE,
    descricao       VARCHAR(105) NOT NULL
) ENGINE = INNODB;

INSERT INTO enum_tipo_segredo (pk_tipo_segredo, nome, descricao) VALUES
    (1, 'Público'     , 'Usuários sem permissão explícita têm acesso de leitura ao segredo e aos seus campos.'                     ),
    (2, 'Encontrável' , 'Usuários sem permissão explícita têm acesso de encontrar o segredo, mas não de visualizar os seus campos.'),
    (3, 'Confidencial', 'Usuários sem permissão explícita não são informados nem mesmo acerca da existência do segredo.'           );

CREATE TABLE IF NOT EXISTS categoria (
    pk_categoria INTEGER       NOT NULL PRIMARY KEY AUTO_INCREMENT,
    nome         VARCHAR(50)   NOT NULL UNIQUE,
    CONSTRAINT nome_min_length CHECK (LENGTH(nome) >= 2)
) ENGINE = INNODB;

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
ALTER TABLE categoria AUTO_INCREMENT = 9;

CREATE TABLE IF NOT EXISTS usuario (
    pk_usuario      INTEGER      NOT NULL PRIMARY KEY AUTO_INCREMENT,
    login           VARCHAR( 50) NOT NULL UNIQUE,
    fk_nivel_acesso INTEGER      NOT NULL,
    hash_com_sal    VARCHAR(144) NOT NULL,
    CONSTRAINT fk_usuario        FOREIGN KEY (fk_nivel_acesso) REFERENCES enum_nivel_acesso (pk_nivel_acesso) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT login_min_length  CHECK       (LENGTH(login       ) >=   4),
    CONSTRAINT hash_length       CHECK       (LENGTH(hash_com_sal)  = 144)
) ENGINE = INNODB;

CREATE TABLE IF NOT EXISTS segredo (
    pk_segredo      INTEGER      NOT NULL PRIMARY KEY AUTO_INCREMENT,
    nome            VARCHAR( 50) NOT NULL,
    descricao       VARCHAR(500) NOT NULL,
    fk_tipo_segredo INTEGER      NOT NULL,
    CONSTRAINT fk_segredo        FOREIGN KEY (fk_tipo_segredo) REFERENCES enum_tipo_segredo (pk_tipo_segredo) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT nome_min_length   CHECK       (LENGTH(nome) >= 4)
) ENGINE = INNODB;

CREATE TABLE IF NOT EXISTS campo_segredo (
    pfk_segredo INTEGER         NOT NULL,
    pk_nome     VARCHAR( 500)   NOT NULL,
    valor       VARCHAR(5000)   NOT NULL,
    PRIMARY KEY (pfk_segredo, pk_nome),
    CONSTRAINT fk_campo_segredo FOREIGN KEY (pfk_segredo) REFERENCES segredo (pk_segredo) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT nome_min_length  CHECK       (LENGTH(pk_nome) >= 1)
) ENGINE = INNODB;

CREATE TABLE IF NOT EXISTS categoria_segredo (
    pfk_segredo   INTEGER NOT NULL,
    pfk_categoria INTEGER NOT NULL,
    PRIMARY KEY (pfk_segredo, pfk_categoria),
    CONSTRAINT fk_categoria_segredo_segredo   FOREIGN KEY (pfk_segredo  ) REFERENCES segredo   (pk_segredo  ) ON DELETE CASCADE  ON UPDATE CASCADE,
    CONSTRAINT fk_categoria_segredo_categoria FOREIGN KEY (pfk_categoria) REFERENCES categoria (pk_categoria) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = INNODB;

CREATE TABLE IF NOT EXISTS permissao (
    pfk_usuario                     INTEGER NOT NULL,
    pfk_segredo                     INTEGER NOT NULL,
    fk_tipo_permissao               INTEGER NOT NULL,
    PRIMARY KEY (pfk_usuario, pfk_segredo),
    CONSTRAINT fk_permissao_usuario FOREIGN KEY (pfk_usuario      ) REFERENCES usuario             (pk_usuario       ) ON DELETE CASCADE  ON UPDATE CASCADE,
    CONSTRAINT fk_permissao_segredo FOREIGN KEY (pfk_segredo      ) REFERENCES segredo             (pk_segredo       ) ON DELETE CASCADE  ON UPDATE CASCADE,
    CONSTRAINT fk_permissao_tipo    FOREIGN KEY (fk_tipo_permissao) REFERENCES enum_tipo_permissao (pk_tipo_permissao) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = INNODB;

INSERT INTO segredo (pk_segredo, nome, descricao, fk_tipo_segredo) VALUES (-1, 'Cofre de senhas', 'Segredos acerca do guardador de segredos.', 2);
INSERT INTO campo_segredo (pfk_segredo, pk_nome, valor) VALUES (-1, 'Chave da sessão', HEX(RANDOM_BYTES(256)));
INSERT INTO categoria_segredo (pfk_segredo, pfk_categoria) VALUES (-1, 2);