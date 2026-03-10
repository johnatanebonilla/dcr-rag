# RAG: Diccionario de Cuervo (Versión Open-Source)

Este módulo permite realizar consultas semánticas y lexicográficas sobre el Diccionario de Cuervo utilizando técnicas de RAG de forma **100% gratuita** (usando modelos locales y el nivel gratuito de Groq).

## Requisitos

- Python 3.8+
- Una clave de API de **Groq** (Gratuita en [console.groq.com](https://console.groq.com/)).

## Instalación

1.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
2.  Crea un archivo `.env` o exporta tu clave de API de Groq:
    ```bash
    # En un archivo .env
    GROQ_API_KEY=gsk_tu_clave_aqui
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

- Cuervo, R. J. (2002). _Diccionario de construcción y régimen de la lengua castellana en CD-ROM_ (1ª ed.). Barcelona: Herder Editorial.
- Instituto Caro y Cuervo. (1954–1994). _Diccionario de construcción y régimen de la lengua castellana_ (Vols. 3–8). Bogotá: Instituto Caro y Cuervo.

---

_Proyecto de preservación y digitalización lexicográfica._
