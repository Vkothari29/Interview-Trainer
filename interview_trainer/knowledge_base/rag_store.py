"""
RAG Layer — builds and queries the ChromaDB vector store from the seed knowledge base.
"""

import json
import os
import warnings
from pathlib import Path
from typing import Optional

# Suppress HuggingFace symlink warning (cosmetic on Windows without Developer Mode)
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
warnings.filterwarnings("ignore", category=FutureWarning, module="sentence_transformers")

import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = Path(__file__).parent.parent / "data" / "chroma_db"
SEED_PATH = Path(__file__).parent.parent / "knowledge_base" / "questions_seed.json"
COLLECTION_NAME = "interview_knowledge"


def _get_embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )


def _get_client() -> chromadb.PersistentClient:
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_PATH))


def build_vector_store() -> chromadb.Collection:
    """Ingest the seed knowledge base into ChromaDB. Safe to call repeatedly (upserts)."""
    client = _get_client()
    ef = _get_embedding_function()
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    with open(SEED_PATH, "r", encoding="utf-8") as f:
        items = json.load(f)

    documents, metadatas, ids = [], [], []
    for item in items:
        # Combine question + model_answer for richer embeddings
        text = f"Question: {item['question']}\nAnswer: {item['model_answer']}"
        documents.append(text)
        metadatas.append(
            {
                "id": item["id"],
                "category": item["category"],
                "role": item["role"],
                "difficulty": item["difficulty"],
                "levels": ",".join(item["level"]),
                "tags": ",".join(item["tags"]),
                "question": item["question"],
                "model_answer": item["model_answer"],
                "tips": json.dumps(item["tips"]),
            }
        )
        ids.append(item["id"])

    collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
    print(f"[RAG] Upserted {len(items)} documents into '{COLLECTION_NAME}'.")
    return collection


def get_collection() -> chromadb.Collection:
    """Return the existing collection (building it if not yet initialised)."""
    client = _get_client()
    ef = _get_embedding_function()
    try:
        collection = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
        if collection.count() == 0:
            return build_vector_store()
        return collection
    except Exception:
        return build_vector_store()


def retrieve_questions(
    query: str,
    role: str = "Software Engineer",
    level: str = "Mid-level",
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    n_results: int = 8,
) -> list[dict]:
    """
    Semantic search over the knowledge base with optional metadata filters.
    Returns a list of question dicts with question, model_answer, tips, category, etc.
    ChromaDB where filters are applied only for simple equality (category, difficulty).
    Level and role filtering is done post-query in Python for compatibility.
    """
    collection = get_collection()

    # Build ChromaDB where clause for simple equality filters only
    where_conditions = []
    if category:
        where_conditions.append({"category": {"$eq": category}})
    if difficulty:
        where_conditions.append({"difficulty": {"$eq": difficulty}})

    query_kwargs = {
        "query_texts": [query],
        "n_results": min(n_results * 3, collection.count()),  # over-fetch, then filter
        "include": ["metadatas", "distances"],
    }
    if len(where_conditions) == 1:
        query_kwargs["where"] = where_conditions[0]
    elif len(where_conditions) > 1:
        query_kwargs["where"] = {"$and": where_conditions}

    results = collection.query(**query_kwargs)

    items = []
    for meta in results["metadatas"][0]:
        # Post-filter by level (comma-separated string e.g. "Junior,Mid-level,Senior")
        item_levels = meta.get("levels", "")
        if level and level not in item_levels:
            continue
        items.append(
            {
                "id": meta["id"],
                "category": meta["category"],
                "question": meta["question"],
                "model_answer": meta["model_answer"],
                "tips": json.loads(meta["tips"]),
                "difficulty": meta["difficulty"],
                "tags": meta["tags"].split(","),
            }
        )
        if len(items) >= n_results:
            break

    # If strict level filtering returned nothing, return all results without level filter
    if not items:
        items = []
        for meta in results["metadatas"][0]:
            items.append(
                {
                    "id": meta["id"],
                    "category": meta["category"],
                    "question": meta["question"],
                    "model_answer": meta["model_answer"],
                    "tips": json.loads(meta["tips"]),
                    "difficulty": meta["difficulty"],
                    "tags": meta["tags"].split(","),
                }
            )
            if len(items) >= n_results:
                break

    return items


def retrieve_all_for_role(
    role: str,
    level: str,
    n_results: int = 12,
) -> list[dict]:
    """Retrieve a balanced, role-relevant question set for the given role + level."""
    query = f"interview questions for {level} {role}"
    return retrieve_questions(query=query, role=role, level=level, n_results=n_results)


if __name__ == "__main__":
    build_vector_store()
    results = retrieve_all_for_role("Software Engineer", "Mid-level", n_results=5)
    for r in results:
        print(f"[{r['category']}][{r['difficulty']}] {r['question'][:80]}...")
