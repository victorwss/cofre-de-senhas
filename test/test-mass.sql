INSERT INTO usuario (login, fk_nivel_acesso, hash_com_sal) VALUES ('Harry Potter', 1, 'SbhhiMEETzPiquOxabc178eb35f26c8f59981b01a11cbec48b16f6a8e2c204f4a9a1b633c9199e0b3b2a64b13e49226306bb451c57c851f3c6e872885115404cb74279db7f5372ea'); -- alohomora
INSERT INTO usuario (login, fk_nivel_acesso, hash_com_sal) VALUES ('Voldemort'   , 0, 'ZisNWkdEImMneIcX8ac8780d30e67df14c1afbaf256e1ee45afd1d3cf2654d154b2e9c63541a40d4132a9beed69c4a47b3f2e5612c2751cdfa3abfaed9797fe54777e2f3dfe6aaa0'); -- avada kedavra
INSERT INTO usuario (login, fk_nivel_acesso, hash_com_sal) VALUES ('Dumbledore'  , 2, 'sMIIsuQpzUZswvbW8bc81f083ae783d5dc4f4ae688b6d41d7c5d4b0da55bdb6f42d07453031c046ed4151d0cead5e647f307f96701e586dbb38e197222b645807f10f7b4c124d68c'); -- expecto patronum
INSERT INTO usuario (login, fk_nivel_acesso, hash_com_sal) VALUES ('Hermione'    , 1, 'VPJWqamYPZTUKxsxe79b2fdd41d88c308f2be7c92432d68c9d55ecc9fb9b277c1424d5626777b6e26067875b5a28f10d64db83e41a7537b21850d1bd8359b8e9bfe68e7acb02ff1d'); -- expelliarmus

INSERT INTO segredo (nome, descricao, fk_tipo_segredo) VALUES ('Dragon Ball Z', 'Segredos acerca de Dragon Ball Z.', 3);
INSERT INTO segredo (nome, descricao, fk_tipo_segredo) VALUES ('Senhor dos Anéis', 'Segredos acerca do Senhor dos Anéis.', 2);
INSERT INTO segredo (nome, descricao, fk_tipo_segredo) VALUES ('Star Wars', 'Guerra nas estrelas.', 1);
INSERT INTO segredo (nome, descricao, fk_tipo_segredo) VALUES ('Openheimer', 'Bomba atômica.', 3);

UPDATE campo_segredo SET valor = '0123456789ABCDEFFEDCBA9876543210' WHERE pfk_segredo = -1 AND pk_nome = 'Chave da sessão';
INSERT INTO campo_segredo (pfk_segredo, pk_nome, valor) VALUES (1, 'Nome do Goku', 'Kakaroto');
INSERT INTO campo_segredo (pfk_segredo, pk_nome, valor) VALUES (1, 'Número de esferas do dragão', '7');
INSERT INTO campo_segredo (pfk_segredo, pk_nome, valor) VALUES (2, 'Nome da montanha dos anões', 'Monte Erebus');
INSERT INTO campo_segredo (pfk_segredo, pk_nome, valor) VALUES (3, 'Nome do imperador', 'Palpatine');
INSERT INTO campo_segredo (pfk_segredo, pk_nome, valor) VALUES (3, 'Nome do cara vestido de preto', 'Darth Vader');
INSERT INTO campo_segredo (pfk_segredo, pk_nome, valor) VALUES (3, 'Robô chato e falastrão', 'C3PO');
INSERT INTO campo_segredo (pfk_segredo, pk_nome, valor) VALUES (4, 'Átomos para fazer bomba', 'Urânio e plutônio');

INSERT INTO categoria_segredo (pfk_segredo, pfk_categoria) VALUES (1, 8);
INSERT INTO categoria_segredo (pfk_segredo, pfk_categoria) VALUES (2, 2);
INSERT INTO categoria_segredo (pfk_segredo, pfk_categoria) VALUES (2, 9);
INSERT INTO categoria_segredo (pfk_segredo, pfk_categoria) VALUES (3, 5);

INSERT INTO permissao (pfk_usuario, pfk_segredo, fk_tipo_permissao) VALUES (1, 1, 1);
INSERT INTO permissao (pfk_usuario, pfk_segredo, fk_tipo_permissao) VALUES (1, 2, 2);
INSERT INTO permissao (pfk_usuario, pfk_segredo, fk_tipo_permissao) VALUES (1, 3, 3);