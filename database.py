import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))


def executar_sql(sql, parametros=(), escrita=True):
    conexao = mysql.connector.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )

    cursor = None

    try:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute(sql, parametros)

        if sql.strip().upper().startswith("SELECT"):
            return cursor.fetchall()

        conexao.commit()
        return {"id_gerado": cursor.lastrowid}
    except Exception:
        if not escrita:
            conexao.rollback()
        else:
            conexao.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conexao.close()
