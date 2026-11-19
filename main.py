import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from mysql.connector import Error as MySQLError

from database import executar_sql

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
    tutores = executar_sql(sql)

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
    pets = executar_sql(sql)

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
