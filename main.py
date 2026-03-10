from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
from consulta import definir, buscar_palabra
import os

app = FastAPI(title="Cuervo RAG API")

class QueryRequest(BaseModel):
    palabra: str

# Obtener ruta absoluta del archivo index.html
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "static", "index.html")

@app.get("/")
def read_root():
    return FileResponse(INDEX_FILE)

@app.get("/status")
def get_status():
    from consulta import index
    status = "OK" if index is not None else "ERROR (Data not loaded)"
    return {
        "database_status": status
    }

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
