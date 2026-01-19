import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

# Import application classes
from .App import App
from .QueryEngine import QueryEngine

app = FastAPI(title="Contract Intelligence API")

# Initialize application logic
logic_app = App()
query_engine = QueryEngine()

# Request model for questions
class QuestionRequest(BaseModel):
    """Model for question requests."""
    question: str

@app.post("/ingest-all")
async def ingest_all_files() -> dict:
    """Execute the ingestion process available in the App class.

    Returns: 
        A message indicating completion.
        
    Raises: 
        HTTPException on failure.
    """
    try:
        logic_app.run()
        return {"message": "Ingestion process completed. Check logs for details."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)) -> dict:
    """Upload an individual file and process it.
    Args: 
        file: PDF file to upload and process.

    Returns: 
        A message indicating success or failure.

    Raises: 
        HTTPException on failure.
    """
    
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    upload_dir = "data/raw"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}") from e
    
    finally:
        await file.close()

    success = logic_app.process_document(file_path)
    
    if success:
        return {
            "status": "success",
            "filename": file.filename,
            "message": "File processed and indexed successfully"
        }
    else:
        raise HTTPException(
            status_code=500, 
            detail=f"File {file.filename} saved but processing failed. Check logs."
        )

@app.post("/ask")
async def ask_question(request: QuestionRequest) -> dict:
    """Endpoint for interacting with contracts.
    Args:
        request: QuestionRequest object containing the user's question.

    Returns:
        A dictionary with the question and the generated answer.

    Raises:        
        HTTPException on failure.
    """
    try:
        answer = query_engine.rag_query(request.question)
        return {"question": request.question, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    