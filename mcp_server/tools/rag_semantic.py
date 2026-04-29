from sentence_transformers import SentenceTransformer
import faiss

with open("semantic_context.txt") as f:
    lines = f.readlines()

model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(lines)

index = faiss.IndexFlatL2(len(embeddings[0]))
index.add(embeddings)

def retrieve_context(question):
    query_vec = model.encode([question])
    D, I = index.search(query_vec, k=5)
    return "\n".join([lines[i] for i in I[0]])