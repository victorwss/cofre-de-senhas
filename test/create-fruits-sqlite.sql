DROP TABLE IF EXISTS animal;
DROP TABLE IF EXISTS juice_2;
DROP TABLE IF EXISTS juice_1;
DROP TABLE IF EXISTS fruit;
DROP TABLE IF EXISTS tree;

CREATE TABLE fruit (
    pk_fruit        INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL UNIQUE      CHECK (LENGTH(name) >= 4 AND LENGTH(name) <= 50)
) STRICT;

INSERT INTO fruit (name) VALUES ('orange');
INSERT INTO fruit (name) VALUES ('strawberry');
INSERT INTO fruit (name) VALUES ('lemon');

CREATE TABLE juice_1 (
    pk_fruit INTEGER NOT NULL PRIMARY KEY,
    FOREIGN KEY (pk_fruit) REFERENCES fruit (pk_fruit) ON DELETE CASCADE ON UPDATE CASCADE
) STRICT;

CREATE TABLE juice_2 (
    pk_fruit INTEGER NOT NULL PRIMARY KEY,
    FOREIGN KEY (pk_fruit) REFERENCES fruit (pk_fruit) ON DELETE RESTRICT ON UPDATE RESTRICT
) STRICT;

CREATE TABLE animal (
    pk_animal INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name      TEXT    NOT NULL UNIQUE      CHECK (LENGTH(name) >= 2 AND LENGTH(name) <= 50),
    gender    TEXT    NOT NULL             CHECK (gender = 'M' OR gender = 'F' OR gender = '-'),
    species   TEXT    NOT NULL             CHECK (LENGTH(species) >= 4 AND LENGTH(species) <= 50),
    age       INTEGER NOT NULL
) STRICT;

INSERT INTO animal (name, gender, species, age) VALUES ('mimosa'   , 'F', 'bos taurus'      , 4);
INSERT INTO animal (name, gender, species, age) VALUES ('rex'      , 'M', 'canis familiaris', 6);
INSERT INTO animal (name, gender, species, age) VALUES ('sylvester', 'M', 'felis catus'     , 8);