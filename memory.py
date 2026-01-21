from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import uuid

client = QdrantClient(url="http://localhost:6333")
model = SentenceTransformer("all-MiniLM-L6-v2")

COLLECTION = "mental_health_memory"

def store_memory(text, mood, session_id):
    vector = model.encode(text).tolist()

    client.upsert(
        collection_name=COLLECTION,
        points=[{
            "id": str(uuid.uuid4()),
            "vector": vector,
            "payload": {
                "text": text,
                "mood": mood,
                "session_id": session_id
            }
        }]
    )

def retrieve_memory(query, session_id, limit=3):
    vector = model.encode(query).tolist()

    results = client.query_points(
        collection_name=COLLECTION,
        query=vector,
        limit=limit,
        with_payload=True
    )

    # manually filter by session_id
    memories = []
    for p in results.points:
        if p.payload.get("session_id") == session_id:
            memories.append(p.payload)

    return memories

    return [p.payload for p in results.points]
def get_user_memories(session_id, limit=50):
    results = client.scroll(
        collection_name=COLLECTION,
        limit=limit,
        with_payload=True,
        scroll_filter={
            "must": [
                {
                    "key": "session_id",
                    "match": {"value": session_id}
                }
            ]
        }
    )
    return [p.payload for p in results[0]]
