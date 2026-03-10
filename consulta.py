import faiss
import json
import numpy as np
from groq import Groq
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Cargar variables de entorno (API Key de Groq)
load_dotenv()
client = Groq()

# Cargar el mismo modelo de embeddings que en la indexación
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Cargar índice y metadatos
index = faiss.read_index("cuervo_index.faiss")
with open("cuervo_meta.json", "r", encoding="utf-8") as f:
    documents = json.load(f)

def buscar_palabra(query, k=5):
    """
    Genera el embedding de la consulta usando el modelo local y recupera los k documentos más cercanos.
    """
    query_embedding = model.encode([query]).astype('float32')
    
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
