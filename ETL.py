"""
Script de Extração e Carga (ETL) - CSV para Banco de Dados MySQL

Este script realiza a leitura de um arquivo CSV de videogames, aplica tratamento e limpeza dos dados,
gera uma chave única por jogo e carrega os dados em um banco MySQL usando SQLAlchemy.

Dependências:
    - pandas
    - re (built-in)
    - sqlalchemy
    - python-dotenv
    - pymysql

Configuração:
    1. Criar um banco MySQL
    2. Configurar variável DATABASE_URL no arquivo .env

Exemplo:
    DATABASE_URL=mysql+pymysql://root:senha@localhost:3306/NomeDoBanco
"""

import hashlib
import os
import re
import unicodedata
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("[ERRO] DATABASE_URL não encontrado no arquivo .env")

FILE_PATH = "vgsales.csv"
HASH_SIZE = 12

_RE_SPACES = re.compile(r"[ \-]+")
_RE_NON_ALNUM = re.compile(r"[^a-z0-9_]")
_RE_MULTI_UND = re.compile(r"_+")

TRADUCAO_COLUNAS = {
    "rank": "ranking",
    "name": "nome",
    "platform": "plataforma",
    "year": "ano",
    "genre": "genero",
    "publisher": "editora",
    "na_sales": "vendas_na",
    "eu_sales": "vendas_eu",
    "jp_sales": "vendas_jp",
    "other_sales": "vendas_outros",
}


def _normalizar_header(header: str) -> str:
    h = unicodedata.normalize("NFKD", header).encode("ASCII", "ignore").decode("ASCII")
    h = h.strip().lower()
    h = _RE_SPACES.sub("_", h)
    h = _RE_NON_ALNUM.sub("", h)
    h = _RE_MULTI_UND.sub("_", h)
    return h.strip("_")


def _gerar_hash(texto) -> str:
    if pd.isna(texto) or str(texto).strip().lower() in ("nan", ""):
        return pd.NA
    return hashlib.md5(str(texto).strip().lower().encode("utf-8")).hexdigest()[:HASH_SIZE]


def extrair(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    return df


def transformar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.replace(r"^\s*$", pd.NA, regex=True)

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = (
            df[col].astype(str)
            .str.replace("\x96", "-", regex=False)
            .str.encode("utf-8", errors="ignore")
            .str.decode("utf-8")
            .str.strip()
            .replace("nan", pd.NA)
        )

    sem_ano = df["ano"].isna() | df["ano"].astype(str).str.strip().str.lower().isin(["nan", "n/a", ""])
    df.loc[~sem_ano, "ano"] = df.loc[~sem_ano, "ano"].astype(float).astype(int)
    df.loc[sem_ano, "ano"] = pd.NA

    df["id_jogo"] = df["nome"].apply(_gerar_hash)
    df["id_lancamento"] = df.apply(
        lambda r: hashlib.md5(
            f"{str(r['nome']).lower()}|{str(r['plataforma']).lower()}|{str(r['ano'])}".encode()
        ).hexdigest()[:HASH_SIZE],
        axis=1,
    )

    return df


def carregar(df: pd.DataFrame, engine, chunk_size: int = 500) -> None:
    jogos = (
        df[["id_jogo", "nome", "genero", "editora"]]
        .drop_duplicates(subset=["id_jogo"])
        .to_dict(orient="records")
    )

    lancamentos = (
        df[["id_lancamento", "id_jogo", "plataforma", "ano", "vendas_na", "vendas_eu", "vendas_jp", "vendas_outros"]]
        .drop_duplicates(subset=["id_lancamento"])
        .to_dict(orient="records")
    )

    def limpar(records):
        return [{k: (None if pd.isna(v) else v) for k, v in r.items()} for r in records]

    with engine.begin() as conn:
        for i in range(0, len(jogos), chunk_size):
            conn.execute(text("""
                INSERT IGNORE INTO jogo (id_jogo, nome, genero, editora)
                VALUES (:id_jogo, :nome, :genero, :editora)
            """), limpar(jogos[i:i+chunk_size]))
        print(f"[BANCO] jogo: {len(jogos)} registros inseridos.")

        for i in range(0, len(lancamentos), chunk_size):
            conn.execute(text("""
                INSERT INTO lancamento (id_lancamento, id_jogo, plataforma, ano, vendas_na, vendas_eu, vendas_jp, vendas_outros)
                VALUES (:id_lancamento, :id_jogo, :plataforma, :ano, :vendas_na, :vendas_eu, :vendas_jp, :vendas_outros)
                ON DUPLICATE KEY UPDATE
                    plataforma=VALUES(plataforma), ano=VALUES(ano),
                    vendas_na=VALUES(vendas_na), vendas_eu=VALUES(vendas_eu),
                    vendas_jp=VALUES(vendas_jp), vendas_outros=VALUES(vendas_outros)
            """), limpar(lancamentos[i:i+chunk_size]))
        print(f"[BANCO] lancamento: {len(lancamentos)} registros inseridos.")


if __name__ == "__main__":
    print("\n[INFO] Iniciando Pipeline ETL: vgsales.csv -> MySQL")

    engine = create_engine(DATABASE_URL)

    print("\n[INFO] Etapa 1/3: Extração")
    df_raw = extrair(FILE_PATH)
    print(f"[OK] {len(df_raw)} registros lidos.")

    print("\n[INFO] Etapa 2/3: Transformação")
    df_limpo = transformar(df_raw)

    print("\n[INFO] Etapa 3/3: Carga")
    carregar(df_limpo, engine)

    print("\n[SUCESSO] Pipeline finalizado.\n")
