DROP TABLE IF EXISTS animal;
DROP TABLE IF EXISTS juice_2;
DROP TABLE IF EXISTS juice_1;
DROP TABLE IF EXISTS fruit;
DROP TABLE IF EXISTS tree;

CREATE TABLE fruit (
    pk_fruit   INTEGER     NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(50) NOT NULL UNIQUE,
    CONSTRAINT name_min_size CHECK (LENGTH(name) >= 4)
) ENGINE = INNODB;

INSERT INTO fruit (name) VALUES ('orange');
INSERT INTO fruit (name) VALUES ('strawberry');
INSERT INTO fruit (name) VALUES ('lemon');

CREATE TABLE juice_1 (
    pk_fruit INTEGER NOT NULL PRIMARY KEY,
    CONSTRAINT FOREIGN KEY (pk_fruit) REFERENCES fruit (pk_fruit) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = INNODB;

CREATE TABLE juice_2 (
    pk_fruit INTEGER NOT NULL PRIMARY KEY,
    CONSTRAINT FOREIGN KEY (pk_fruit) REFERENCES fruit (pk_fruit) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = INNODB;

CREATE TABLE animal (
    pk_animal INTEGER     NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name      VARCHAR(50) NOT NULL                UNIQUE,
    gender    CHAR(1)     NOT NULL,
    species   VARCHAR(50) NOT NULL,
    age       INTEGER     NOT NULL,
    CONSTRAINT name_min_size CHECK (LENGTH(name) >= 2),
    CONSTRAINT gener_domain  CHECK (gender = 'M' OR gender = 'F' OR gender = '-'),
    CONSTRAINT species_size  CHECK (LENGTH(species) >= 4)
) ENGINE = INNODB;

INSERT INTO animal (name, gender, species, age) VALUES ('mimosa'   , 'F', 'bos taurus'      , 4);
INSERT INTO animal (name, gender, species, age) VALUES ('rex'      , 'M', 'canis familiaris', 6);
INSERT INTO animal (name, gender, species, age) VALUES ('sylvester', 'M', 'felis catus'     , 8);