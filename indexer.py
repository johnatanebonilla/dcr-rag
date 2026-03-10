import os
import json
import numpy as np
import faiss
import re
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Cargar el modelo de embeddings open-source (soporta español)
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def get_text_from_entry(data):
    """
    Formatea la entrada del diccionario en el esquema requerido para el RAG.
    """
    palabra = data.get('lema', 'Sin lema')
    # Limpiar HTML si es necesario (el prompt del LLM se encargará del resto,
    # pero para el embedding es mejor texto limpio).
    palabra_clean = re.sub(r'<[^>]+>', '', palabra).strip()
    
    definiciones = []
    ejemplos = []
    
    if data.get('introduccion'):
        definiciones.append(re.sub(r'<[^>]+>', '', data['introduccion']))
    
    for acep in data.get('acepciones', []):
        def_text = re.sub(r'<[^>]+>', '', acep.get('definicion', ''))
        if def_text:
            definiciones.append(f"{acep.get('id', '')} {def_text}")
        
        for cita in acep.get('ejemplos_citas', []):
            txt = re.sub(r'<[^>]+>', '', cita.get('texto_cita', ''))
            if txt: ejemplos.append(txt)
            
        for sub in acep.get('subacepciones', []):
            s_def = re.sub(r'<[^>]+>', '', sub.get('definicion', ''))
            if s_def:
                definiciones.append(f"{sub.get('id_limpio', '')} {s_def}")
            for s_cita in sub.get('ejemplos_citas', []):
                s_txt = re.sub(r'<[^>]+>', '', s_cita.get('texto_cita', ''))
                if s_txt: ejemplos.append(s_txt)

    if data.get('construccion_sintactica'):
        definiciones.append("Construcción: " + re.sub(r'<[^>]+>', '', data['construccion_sintactica']))

    doc = f"PALABRA: {palabra_clean}\n\n"
    doc += "DEFINICIÓN:\n" + "\n".join(definiciones) + "\n\n"
    doc += "EJEMPLOS:\n" + "\n".join(ejemplos)
    return doc

import re # Requerido dentro de la función o arriba

def create_index(json_path, output_index="cuervo_index.faiss", output_meta="cuervo_meta.json"):
    files = [f for f in os.listdir(json_path) if f.endswith('.json') and not f.startswith('_') and f != 'index_db.json']
    
    documents = []
    print(f"Leyendo {len(files)} archivos JSON...")
    for f in tqdm(files):
        with open(os.path.join(json_path, f), 'r', encoding='utf-8') as file:
            data = json.load(file)
            documents.append(get_text_from_entry(data))
            
    print(f"Generando embeddings (HuggingFace: paraphrase-multilingual-MiniLM-L12-v2)...")
    # SentenceTransformers maneja lotes automáticamente
    embeddings = model.encode(documents, show_progress_bar=True)
    
    embeddings = np.array(embeddings).astype('float32')
    
    # Crear índice FAISS (L2 distance por defecto o Inner Product si normalizamos)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # Guardar índice
    faiss.write_index(index, output_index)
    
    # Guardar metadatos (los textos correspondientes a cada ID del índice)
    with open(output_meta, 'w', encoding='utf-8') as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)
    
    print(f"Indexación completada. Guardado en {output_index} y {output_meta}")

if __name__ == "__main__":
    # Ajustar ruta segun ubicación del script
    JSON_DIR = "../json"
    create_index(JSON_DIR)
