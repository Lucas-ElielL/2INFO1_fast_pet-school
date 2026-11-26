import logging

from fastapi import FastAPI, HTTPException, Path, Request, Response
from fastapi.responses import JSONResponse
from mysql.connector import Error as MySQLError

from database import executar_sql
from schemas import petEntrada, tutorEntrada

app = FastAPI(title="API de pets e tutores — Projeto Integrador II")


@app.exception_handler(MySQLError)
def erro_de_banco(request: Request, exc: MySQLError):
    logging.getLogger("uvicorn.error").error("Erro no MySQL: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Não foi possível acessar o banco de dados."},
    )


def representar_tutor(tutor):
    return {
        "id": tutor["tutor_id"],
        "nome": tutor["nome"],
        "email": tutor["email"],
    }


@app.get("/tutores")
def listar_tutores():
    sql = "SELECT tutor_id, nome, email FROM tutores ORDER BY tutor_id"
    tutores = executar_sql(sql, escrita=False)

    return {
        "dados": [representar_tutor(tutor) for tutor in tutores],
        "didatica": {"sql": sql, "parametros": []},
    }


@app.get("/tutores/{tutor_id}")
def buscar_tutor_por_id(tutor_id: int):
    sql = "SELECT tutor_id, nome, email FROM tutores WHERE tutor_id = %s"
    tutores = executar_sql(sql, (tutor_id,))

    if not tutores:
        raise HTTPException(
            status_code=404,
            detail="Tutor não encontrado.",
        )

    return {"dados": representar_tutor(tutores[0])}


@app.get("/pets")
def listar_pets():
    sql = "SELECT pet_id, nome, especie, tutorId FROM pets ORDER BY pet_id"
    pets = executar_sql(sql, escrita=False)

    return {
        "dados": [
            {
                "id": pet["pet_id"],
                "nome": pet["nome"],
                "especie": pet["especie"],
                "tutor_id": pet["tutorId"],
            }
            for pet in pets
        ],
        "didatica": {"sql": sql, "parametros": []},
    }


@app.get("/pets/{pet_id}")
def buscar_pet_por_id(pet_id: int):
    sql = "SELECT pet_id, nome, especie, tutorId FROM pets WHERE pet_id = %s"
    pets = executar_sql(sql, (pet_id,))

    if not pets:
        raise HTTPException(
            status_code=404,
            detail="Pet não encontrado.",
        )

    pet = pets[0]
    return {
        "dados": {
            "id": pet["pet_id"],
            "nome": pet["nome"],
            "especie": pet["especie"],
            "tutor_id": pet["tutorId"],
        }
    }


@app.post("/pets", status_code=201)
def criar_pet(pet: petEntrada, response: Response):
    sql = """INSERT INTO pets (nome, especie, tutorId) VALUES (%s, %s, %s)""".strip()

    parametros = (pet.nome, pet.especie, pet.tutor_id)
    resultado = executar_sql(sql, parametros)
    pet_id = resultado["id_gerado"]

    response.headers["Location"] = f"/pets/{pet_id}"

    return {
        "dados": {
            "id": pet_id,
            "nome": pet.nome,
            "especie": pet.especie,
            "tutor_id": pet.tutor_id,
        },
        "didatica": {"sql": sql, "parametros": parametros},
    }


@app.post("/tutores", status_code=201)
def criar_tutor(tutor: tutorEntrada, response: Response):
    sql = """INSERT INTO tutores (nome, email) VALUES (%s, %s)""".strip()

    parametros = (tutor.nome, tutor.email)
    resultado = executar_sql(sql, parametros)
    tutor_id = resultado["id_gerado"]

    response.headers["Location"] = f"/tutores/{tutor_id}"

    return {
        "dados": {
            "id": tutor_id,
            "nome": tutor.nome,
            "email": tutor.email,
        },
        "didatica": {"sql": sql, "parametros": parametros},
    }


@app.put("/pets/{pet_id}")
def atualizar_pet(pet: petEntrada, pet_id: int = Path(gt=0)):
    sql_select = "SELECT pet_id FROM pets WHERE pet_id = %s"
    existentes = executar_sql(sql_select, (pet_id,), escrita=False)

    if not existentes:
        raise HTTPException(
            status_code=404,
            detail="Pet não encontrado.",
        )

    sql_update = (
        "UPDATE pets SET nome = %s, especie = %s, tutorId = %s WHERE pet_id = %s"
    )
    parametros_update = (pet.nome, pet.especie, pet.tutor_id, pet_id)

    executar_sql(sql_update, parametros_update, escrita=True)

    return {
        "dados": {
            "id": pet_id,
            "nome": pet.nome,
            "especie": pet.especie,
            "tutor_id": pet.tutor_id,
        },
        "didatica": {
            "sql": sql_update,
            "parametros": parametros_update,
        },
    }
