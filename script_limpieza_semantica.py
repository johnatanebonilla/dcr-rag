"""
Script de Limpieza Semántica: Diccionario Cuervo
------------------------------------------------
Lee los archivos JSON del diccionario que aún contienen etiquetas HTML incrustadas,
extrae únicamente el texto estructural (lema, acepciones, citas, autores) y genera
nuevos archivos JSON "puros" (puramente semánticos, sin etiquetas de presentación).

Dependencias:
pip install beautifulsoup4
"""

import os
import glob
import json
import re
from bs4 import BeautifulSoup

def clean_html(text):
    if not text:
        return ""
    # Usar BeautifulSoup para extraer texto y reemplazar etiquetas por espacios si es necesario
    soup = BeautifulSoup(text, 'html.parser')
    clean = soup.get_text(separator=' ')
    # Limpiar espacios múltiples o saltos de línea erráticos
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def extract_autor_ref_from_cita(texto_html, autor_raw, ref_raw):
    # Ya los campos autor_raw y ref_raw están separados en el json original,
    # pero pueden contener etiquetas de formato. Los limpiamos.
    texto = clean_html(texto_html)
    autor = clean_html(autor_raw)
    ref = clean_html(ref_raw)
    return {
        "texto_cita": texto,
        "autor": autor,
        "referencia_obra": ref
    }

def process_file(in_path, out_path):
    with open(in_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    sem_data = {
        "lema": clean_html(data.get("lema", "")),
        "categoria_gramatical": clean_html(data.get("categoria_gramatical", "")),
        "introduccion": clean_html(data.get("introduccion", "")),
        "acepciones": [],
        "etimologia": clean_html(data.get("etimologia", ""))
    }
    
    if "construccion_sintactica" in data:
        sem_data["construccion_sintactica"] = clean_html(data["construccion_sintactica"])

    for acep in data.get("acepciones", []):
        sem_acep = {
            "id": clean_html(acep.get("id", "")),
            "definicion": clean_html(acep.get("definicion", "")),
            "ejemplos_citas": [],
            "subacepciones": []
        }
        
        for cita in acep.get("ejemplos_citas", []):
            sem_cita = extract_autor_ref_from_cita(
                cita.get("texto_cita",""), 
                cita.get("autor",""), 
                cita.get("referencia_obra","")
            )
            sem_acep["ejemplos_citas"].append(sem_cita)
            
        for sub in acep.get("subacepciones", []):
            # Preferir id_limpio, hacer un respaldo hacia id_marcador_html limpio
            id_marcador = sub.get("id_limpio", clean_html(sub.get("id_marcador_html", "")))
            
            sem_sub = {
                "id_marcador": clean_html(id_marcador),
                "definicion": clean_html(sub.get("definicion", "")),
                "ejemplos_citas": []
            }
            
            for cita in sub.get("ejemplos_citas", []):
                sem_cita = extract_autor_ref_from_cita(
                    cita.get("texto_cita",""), 
                    cita.get("autor",""), 
                    cita.get("referencia_obra","")
                )
                sem_sub["ejemplos_citas"].append(sem_cita)
            
            sem_acep["subacepciones"].append(sem_sub)
            
        sem_data["acepciones"].append(sem_acep)
        
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(sem_data, f, ensure_ascii=False, indent=2)

def main():
    in_dir = r'd:\ICC-2026\pasantía\cuervo\json'
    out_dir = r'd:\ICC-2026\pasantía\cuervo\json_semantico'
    os.makedirs(out_dir, exist_ok=True)
    
    files = glob.glob(os.path.join(in_dir, '*.json'))
    # Excluir archivos de índices si existen
    files = [f for f in files if not f.endswith('index_db.json') and not f.endswith('_index.json')]
    
    print(f"Encontrados {len(files)} archivos para procesar...")
    
    index_lemas = []
    
    for count, f in enumerate(files):
        fname = os.path.basename(f)
        out_path = os.path.join(out_dir, fname)
        process_file(f, out_path)
        
        if (count + 1) % 250 == 0:
            print(f"Procesados {count+1}/{len(files)}")
            
    print("Creando índice semántico...")
    for f in glob.glob(os.path.join(out_dir, '*.json')):
        if os.path.basename(f) in ['index_db.json', '_index.json']:
            continue
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if data.get("lema"):
                index_lemas.append({
                    "lema": data["lema"],
                    "file": os.path.basename(f)
                })
                
    index_lemas.sort(key=lambda x: x['lema'].lower())
    
    with open(os.path.join(out_dir, 'index_db.json'), 'w', encoding='utf-8') as idx_f:
        json.dump(index_lemas, idx_f, ensure_ascii=False, indent=2)

    print(f"Migración completada. Guardados en {out_dir}")

if __name__ == '__main__':
    main()
