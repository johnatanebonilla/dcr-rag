from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from consulta import definir, buscar_palabra
import os

app = FastAPI(title="Cuervo RAG API")

class QueryRequest(BaseModel):
    palabra: str

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de RAG del Diccionario de Cuervo"}

@app.post("/definir")
def api_definir(request: QueryRequest):
    try:
        resultado = definir(request.palabra)
        return {"resultado": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/buscar")
def api_buscar(request: QueryRequest):
    try:
        contexto = buscar_palabra(request.palabra)
        return {"contexto": contexto}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
