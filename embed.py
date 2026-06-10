"""
Milestone 4: Embedding and retrieval.

Embeds the chunks from chunks.json with all-MiniLM-L6-v2 and stores them in
a local ChromaDB collection (cosine distance) with source metadata. Exposes
retrieve(query, k) for semantic search.

Run directly to (re)build the index and test retrieval on sample queries:
    python embed.py
"""

import json

import chromadb
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
CHUNKS_FILE = "chunks.json"
DB_DIR = "chroma_db"
COLLECTION_NAME = "unofficial_guide"

# Load the embedding model and persistent vector store once at import time.
_model = SentenceTransformer(MODEL_NAME)
_client = chromadb.PersistentClient(path=DB_DIR)


def build_index():
    """Embed every chunk and (re)load it into ChromaDB with source metadata."""
    with open(CHUNKS_FILE, encoding="utf-8") as f:
        chunks = json.load(f)

    texts = [c["text"] for c in chunks]
    embeddings = _model.encode(texts, show_progress_bar=True).tolist()

    # Start fresh so re-runs don't duplicate or stale-out the collection.
    try:
        _client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = _client.create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # cosine distance: 0 = identical
    )

    collection.add(
        ids=[f"{c['source']}#{c['chunk_index']}" for c in chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[
            {"source": c["source"], "chunk_index": c["chunk_index"]}
            for c in chunks
        ],
    )
    print(f"Indexed {collection.count()} chunks into '{COLLECTION_NAME}'")
    return collection


def retrieve(query, k=4):
    """Return the top-k most similar chunks to query, with sources + distances."""
    collection = _client.get_collection(COLLECTION_NAME)
    query_embedding = _model.encode([query]).tolist()
    result = collection.query(query_embeddings=query_embedding, n_results=k)

    hits = []
    for doc, meta, dist in zip(
        result["documents"][0],
        result["metadatas"][0],
        result["distances"][0],
    ):
        hits.append({
            "text": doc,
            "source": meta["source"],
            "chunk_index": meta["chunk_index"],
            "distance": dist,
        })
    return hits


if __name__ == "__main__":
    build_index()

    # Test retrieval on 3 of the 5 evaluation questions (planning.md).
    test_queries = [
        "Which dining hall is ranked the best at Vanderbilt and why?",
        "How much do Vanderbilt students pay per meal on the meal plan?",
        "What new meal swipe limit did Campus Dining add and at which locations?",
    ]

    for query in test_queries:
        print("\n" + "=" * 75)
        print(f"QUERY: {query}")
        for hit in retrieve(query):
            print(f"\n  [dist {hit['distance']:.3f}] {hit['source']} "
                  f"#{hit['chunk_index']}")
            print(f"  {hit['text'][:220]}")
