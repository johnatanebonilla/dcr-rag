import faiss
import json
import numpy as np
import requests
import time
from groq import Groq
from dotenv import load_dotenv

# Cargar variables de entorno (API Key de Groq y Hugging Face)
load_dotenv()
client = Groq()

HF_API_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
MODEL_ID = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
HF_API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"

# Cargar índice y metadatos
index = faiss.read_index("cuervo_index.faiss")
with open("cuervo_meta.json", "r", encoding="utf-8") as f:
    documents = json.load(f)

def get_embeddings_hf(texts):
    """
    Obtiene embeddings a través de la API de Hugging Face (ligero para Vercel).
    """
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": texts, "options": {"wait_for_model": True}}
    
    for _ in range(3): # Reintentos si la API está cargando
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()
        time.sleep(2)
        
    raise Exception(f"Error en HF API: {response.text}")

def buscar_palabra(query, k=5):
    """
    Genera el embedding de la consulta usando la API y recupera los k documentos más cercanos.
    """
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
