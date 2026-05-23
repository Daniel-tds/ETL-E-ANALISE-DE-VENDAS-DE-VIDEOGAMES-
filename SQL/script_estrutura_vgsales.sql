CREATE DATABASE vgsales;
USE vgsales;

CREATE TABLE jogo (
    id_jogo   CHAR(12)     NOT NULL,
    nome      VARCHAR(200) NOT NULL,
    genero    VARCHAR(20),
    editora   VARCHAR(100),
    PRIMARY KEY (id_jogo)
);

CREATE TABLE lancamento (
    id_lancamento  CHAR(12)    NOT NULL,
    id_jogo        CHAR(12)    NOT NULL,
    plataforma     VARCHAR(20),
    ano            YEAR,
    vendas_na      DECIMAL(8,2),
    vendas_eu      DECIMAL(8,2),
    vendas_jp      DECIMAL(8,2),
    vendas_outros  DECIMAL(8,2),
    PRIMARY KEY (id_lancamento),
    CONSTRAINT fk_jogo_lancamento FOREIGN KEY (id_jogo) REFERENCES jogo(id_jogo) ON DELETE RESTRICT
);