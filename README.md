# RAG: Diccionario de Cuervo (Versión Open-Source)

Este módulo permite realizar consultas semánticas y lexicográficas sobre el **Diccionario de Construcción y Régimen de la Lengua Castellana** utilizando técnicas de RAG de forma **100% gratuita**.

Los datos han sido extraídos del **Diccionario de construcción y régimen de la lengua castellana en CD-ROM** (1ª ed.). Barcelona: Herder Editorial.

## Requisitos

- Python 3.8+
- Una clave de API de **Groq** (Gratuita en [console.groq.com](https://console.groq.com/)).
- Un token de **Hugging Face** (Gratuito en [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)).

## Instalación

1.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
2.  Crea un archivo `.env` con tus claves:
    ```bash
    GROQ_API_KEY=gsk_tu_clave_aqui
    HUGGINGFACE_API_KEY=hf_tu_token_aqui
    ```

## Uso

### 1. Indexación

Para generar los embeddings locales y el índice FAISS, ejecuta:

```bash
python indexer.py
```

_Este proceso usará el modelo `paraphrase-multilingual-MiniLM-L12-v2` (HuggingFace) para generar vectores locales. No consume créditos._

### 2. Consulta

Para obtener una definición académica generada por Llama-3:

```bash
python consulta.py "palabra_a_buscar"
```

## Arquitectura

- **Embeddings**: `SentenceTransformers (HuggingFace)` - Local y gratuito.
- **Base Vectorial**: `FAISS` (Local).
- **LLM**: `Llama-3 (vía Groq)` - Gratuito y de alto rendimiento.
- **Contexto**: Recupera los 5 fragmentos más relevantes.

## Créditos y Citación

Este desarrollo ha sido realizado por **Johnatan E. Bonilla** en el marco del proyecto **“Observatorio Ecosistema Digital de Lenguas de Colombia”**, que es del **Grupo de Investigaciones** de la **Línea de investigación en Lingüística de Corpus y Computacional** del **Instituto Caro y Cuervo**.

Si utilizas estos datos o esta herramienta en una investigación académica, por favor cita tanto el desarrollo técnico como las fuentes originales:

### Desarrollo Técnico

- Bonilla, J. E. (2026). _Cuervo RAG: Sistema de recuperación y generación para el Diccionario de Construcción y Régimen en CD-ROM_. [https://github.com/johnatanebonilla/dcr-rag](https://github.com/johnatanebonilla/dcr-rag)

### Fuentes Originales

- Cuervo, R. J. (1886). _Diccionario de construcción y régimen de la lengua castellana_. París: Roger.
- Cuervo, R. J. (2002). _Diccionario de construcción y régimen de la lengua castellana en CD-ROM_ (1ª ed.). Barcelona: Herder Editorial.
- Instituto Caro y Cuervo. (1954–1994). _Diccionario de construcción y régimen de la lengua castellana_ (Vols. 3–8). Bogotá: Instituto Caro y Cuervo.

---

_Proyecto de preservación y digitalización lexicográfica._
