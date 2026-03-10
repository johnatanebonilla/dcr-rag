import faiss
import json
import numpy as np
import requests
import time
import os
from groq import Groq
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
client = Groq()

HF_API_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
MODEL_ID = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
# Usamos el endpoint v1/embeddings que es el estándar más robusto de Hugging Face
HF_API_URL = "https://router.huggingface.co/hf-inference/v1/embeddings"

# Configuración de rutas robustas para Vercel
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "cuervo_index.faiss")
META_PATH = os.path.join(BASE_DIR, "cuervo_meta.json")

# Cargar índice y metadatos
try:
    if not os.path.exists(INDEX_PATH):
        print(f"ERROR: No se encuentra el índice en {INDEX_PATH}")
    index = faiss.read_index(INDEX_PATH)
    
    if not os.path.exists(META_PATH):
        print(f"ERROR: No se encuentran los metadatos en {META_PATH}")
    with open(META_PATH, "r", encoding="utf-8") as f:
        documents = json.load(f)
    print("Índice y metadatos cargados correctamente.")
except Exception as e:
    print(f"EXCEPCIÓN CRÍTICA AL CARGAR DATOS: {str(e)}")
    index = None
    documents = []

def get_embeddings_hf(texts):
    """
    Obtiene embeddings a través de la API compatible con OpenAI de Hugging Face.
    """
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_ID,
        "input": texts
    }
    
    for _ in range(3): # Reintentos si la API está cargando el modelo
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            # Extraer vectores del formato OpenAI: {"data": [{"embedding": [...]}, ...]}
            return [item["embedding"] for item in data["data"]]
        
        # Si el modelo está en cola o cargando, esperamos un poco
        if response.status_code == 503 or "loading" in response.text.lower():
            time.sleep(5)
            continue
        break
        
    raise Exception(f"Error en HF API: {response.text}")

def buscar_palabra(query, k=5):
    """
    Genera el embedding de la consulta usando la API y recupera los k documentos más cercanos.
    """
    if not index:
        raise Exception("El servidor no ha podido cargar la base de datos de conocimiento (FAISS).")
    
    if not HF_API_TOKEN:
        raise Exception("Falta la variable de entorno HUGGINGFACE_API_KEY.")

    embeddings = get_embeddings_hf([query])
    query_embedding = np.array(embeddings).astype('float32')
    
    # Buscar en FAISS
    distances, indices = index.search(query_embedding, k)
    
    # Recuperar los textos correspondientes
    contexto = []
    for idx in indices[0]:
        if idx != -1:
            contexto.append(documents[idx])
    
    return contexto

def definir(palabra):
    """
    Función de inferencia: recupera contexto y llama al LLM para generar la respuesta.
    """
    # 1. Recuperar contexto
    contexto_recuperado = buscar_palabra(palabra)
    contexto_str = "\n---\n".join(contexto_recuperado)
    
    # 2. Generación con LLM usando Groq (Llama 3 es excelente y gratuito)
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": (
                "Eres un lexicógrafo especializado en el Diccionario de Cuervo.\n"
                "Responde usando exclusivamente las entradas recuperadas del diccionario.\n"
                "No resumas ni inventes información.\n"
                "Si existe la entrada, reproduce la definición completa.\n"
                "Si hay varias acepciones, muéstralas numeradas.\n"
                "Conserva el tono académico del diccionario."
            )},
            {"role": "user", "content": (
                f"PALABRA CONSULTADA:\n{palabra}\n\n"
                f"ENTRADAS DEL DICCIONARIO:\n{contexto_str}\n\n"
                "TAREA:\nProporciona la definición completa de la palabra según el diccionario."
            )}
        ],
        temperature=0
    )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query_word = " ".join(sys.argv[1:])
        print(f"\nGenerando definición para: {query_word}...\n")
        resultado = definir(query_word)
        print(resultado)
    else:
        print("Uso: python consulta.py [palabra]")
