from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path

from rag_pipeline import process_document, answer_question


app = FastAPI(title="RAG Document Q&A API")


# Allow the React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Folder where uploaded PDFs are stored
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {
        "message": "RAG Document Q&A API is running!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    # Only allow PDF files
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are currently supported"
        )

    # Save uploaded file
    file_path = UPLOAD_DIR / file.filename

    contents = await file.read()

    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    try:
        # Process the document through the RAG pipeline
        result = process_document(str(file_path))

        return {
            "filename": file.filename,
            "message": "Document processed successfully",
            "characters": result["characters"],
            "chunks": result["chunks"],
            "source": result["source"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )


@app.post("/ask")
def ask_question(request: QuestionRequest):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        # Send question through the RAG pipeline
        result = answer_question(request.question)

        return {
            "question": request.question,
            "answer": result["answer"],
            "sources": result["sources"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating answer: {str(e)}"
        )