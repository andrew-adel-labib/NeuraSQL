import os
import json
import faiss
import numpy as np

from sentence_transformers import (
    SentenceTransformer
)

from mcp_server.tools.schema_retriever import (
    retrieve_schema
)


MODEL_NAME = "all-MiniLM-L6-v2"

TOP_K = 5


embedding_model = SentenceTransformer(
    MODEL_NAME
)


schema = retrieve_schema()


def build_semantic_chunks():

    chunks = []

    for table in schema.get(
        "tables",
        []
    ):

        table_name = table.get(
            "name"
        )

        columns = table.get(
            "columns",
            []
        )

        chunk = f"""
Table: {table_name}

Columns:
{", ".join(columns)}
"""

        chunks.append(chunk)

    return chunks


semantic_chunks = build_semantic_chunks()


embeddings = embedding_model.encode(
    semantic_chunks,
    convert_to_numpy=True
)


dimension = embeddings.shape[1]


index = faiss.IndexFlatL2(
    dimension
)

index.add(
    np.array(
        embeddings,
        dtype=np.float32
    )
)


def retrieve_context(
    question: str,
    top_k: int = TOP_K
):

    query_embedding = embedding_model.encode(
        [question],
        convert_to_numpy=True
    )

    distances, indices = index.search(
        np.array(
            query_embedding,
            dtype=np.float32
        ),
        top_k
    )

    retrieved_chunks = []

    for idx in indices[0]:

        if idx < len(
            semantic_chunks
        ):

            retrieved_chunks.append(
                semantic_chunks[idx]
            )

    return "\n\n".join(
        retrieved_chunks
    )


def retrieve_ranked_schema(
    question: str,
    top_k: int = TOP_K
):

    context = retrieve_context(
        question,
        top_k=top_k
    )

    return {
        "question": question,
        "context": context,
        "top_k": top_k
    }


if __name__ == "__main__":

    while True:

        q = input(
            "\nAsk Question: "
        )

        ctx = retrieve_context(q)

        print("\nRetrieved Context:\n")

        print(ctx)