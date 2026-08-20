from pdf_reader import extract_text_from_pdf
from chunker import split_text
from embeddings import generate_embedding
from vectorstore import add_chunks, search_chunks
from llm import generate_answer

import os


def process_document(file_path: str):
    """
    Process a PDF document and store its chunks
    and embeddings in the vector database.
    """

    # 1. Extract text from PDF
    text = extract_text_from_pdf(file_path)

    # 2. Split text into chunks
    chunks = split_text(text)

    # 3. Generate embeddings
    embeddings = [
        generate_embedding(chunk).tolist()
        for chunk in chunks
    ]

    # 4. Get the original PDF filename
    source_name = os.path.basename(file_path)

    # 5. Store chunks, embeddings, and source metadata
    add_chunks(
        chunks,
        embeddings,
        source_name=source_name
    )

    return {
        "characters": len(text),
        "chunks": len(chunks),
        "source": source_name
    }


def retrieve_relevant_chunks(question: str, n_results=3):
    """
    Retrieve the most relevant document chunks
    for a user's question.
    """

    # 1. Convert question into an embedding
    query_embedding = generate_embedding(question).tolist()

    # 2. Search the vector database
    results = search_chunks(
        query_embedding,
        n_results=n_results
    )

    # 3. Safely get documents
    documents = results.get("documents", [[]])

    if not documents or not documents[0]:
        return []

    documents = documents[0]

    # 4. Safely get metadata
    metadatas = results.get("metadatas", [[]])

    if not metadatas or not metadatas[0]:
        metadatas = [{} for _ in documents]
    else:
        metadatas = metadatas[0]

    # 5. Combine documents with metadata
    retrieved_chunks = []

    for index, document in enumerate(documents):

        metadata = {}

        if index < len(metadatas) and metadatas[index]:
            metadata = metadatas[index]

        retrieved_chunks.append(
            {
                "text": document,
                "source": metadata.get(
                    "source",
                    "Unknown document"
                ),
                "chunk_index": metadata.get(
                    "chunk_index",
                    index
                )
            }
        )

    return retrieved_chunks


def answer_question(question: str):
    """
    Answer a question using retrieved document context
    and the local Qwen model.
    """

    # 1. Retrieve relevant chunks
    retrieved_chunks = retrieve_relevant_chunks(
        question,
        n_results=4
    )

    # 2. Handle no results
    if not retrieved_chunks:
        return {
            "answer": (
                "I could not find relevant information "
                "in the provided documents."
            ),
            "sources": []
        }

    # 3. Build context for the LLM
    context_parts = []

    for chunk in retrieved_chunks:

        source = chunk["source"]
        text = chunk["text"]

        context_parts.append(
            f"[Source: {source}]\n{text}"
        )

    context = "\n\n".join(context_parts)

    # 4. Create the RAG prompt
    prompt = f"""
You are a document question-answering assistant.

Your job is to answer the user's question using ONLY the
information contained in the provided document context.

IMPORTANT RULES:

1. Carefully read ALL provided context.

2. If the question asks for a list, include ALL relevant
   items found in the context.

3. Do not mention only one item when multiple relevant
   items are present.

4. Do not invent, assume, or add information that is
   not present in the document context.

5. If the answer cannot be found in the provided context,
   say exactly:
   "I could not find the answer in the provided documents."

6. Give a clear and concise answer.

7. If information comes from multiple documents,
   combine the information accurately.

8. Do not use outside knowledge.

DOCUMENT CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""

    # 5. Generate answer using local LLM
    answer = generate_answer(prompt)

    # 6. Collect unique source filenames
    sources = []

    for chunk in retrieved_chunks:

        source = chunk["source"]

        if source not in sources:
            sources.append(source)

    # 7. Return answer + sources
    return {
        "answer": answer,
        "sources": sources
    }