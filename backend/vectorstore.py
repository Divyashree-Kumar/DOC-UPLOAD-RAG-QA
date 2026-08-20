import chromadb

client = chromadb.PersistentClient(path="../chroma_db")

collection = client.get_or_create_collection(
    name="documents"
)


def add_chunks(chunks, embeddings, source_name="Unknown document"):
    """
    Add document chunks and embeddings to ChromaDB
    with source information.
    """

    # Remove existing chunks for this document
    try:
        collection.delete(
            where={"source": source_name}
        )
    except Exception:
        pass

    ids = [
        f"{source_name}_chunk_{i}"
        for i in range(len(chunks))
    ]

    metadatas = [
        {
            "source": source_name,
            "chunk_index": i
        }
        for i in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )


def search_chunks(query_embedding, n_results=8):
    """
    Search ChromaDB for the most relevant chunks.
    """

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results