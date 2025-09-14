from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .database import init_db, get_session
from . import crud, llm_client
from dotenv import load_dotenv
from sqlmodel import Session
import pdfplumber
import io
import re
import json
load_dotenv()

app = FastAPI(title="DeepKlarity Resume Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] for all
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.on_event("startup")
def on_startup():
    init_db()

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)

def quick_extract_contact_info(text: str):
    # Very simple regex helpers to fill name/email/phone if possible
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    phone_match = re.search(r'(\+?\d{1,3}[-\s]?)?(\(?\d{2,4}\)?[-\s]?)?\d{3,4}[-\s]?\d{3,4}', text)
    # For name we attempt to use first line heuristics
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    name = None
    if lines:
        candidate = lines[0]
        # If first line contains an email, skip
        if not re.search(r'@', candidate) and len(candidate.split()) <= 4:
            name = candidate
    email = email_match.group(0) if email_match else None
    phone = phone_match.group(0) if phone_match else None
    return name, email, phone

@app.post("/api/upload")
async def upload_resume(file: UploadFile = File(...), session: Session = Depends(get_session)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF supported")
    file_bytes = await file.read()
    text = extract_text_from_pdf(file_bytes)
    name, email, phone = quick_extract_contact_info(text)

    try:
        structured = llm_client.extract_structured_data(text)
    except Exception as e:
        print("=== ERROR IN EXTRACTION ===", e)
        raise HTTPException(status_code=500, detail=f"LLM extraction failed: {e}")

    try:
        analysis = llm_client.analyze_resume(structured)
    except Exception as e:
        print("=== ERROR IN ANALYSIS ===", e)
        raise HTTPException(status_code=500, detail=f"LLM analysis failed: {e}")

    try:
        r = crud.create_resume(session, file.filename, structured, analysis, name, email, phone)
    except Exception as e:
        print("=== ERROR IN DB SAVE ===", e)
        raise HTTPException(status_code=500, detail=f"Database save failed: {e}")

    return {
        "id": r.id,
        "filename": r.filename,
        "name": r.name,
        "email": r.email,
        "phone": r.phone,
        "extracted_data": structured,
        "llm_analysis": analysis
    }


@app.get("/api/resumes")
def list_resumes(session: Session = Depends(get_session)):
    rows = crud.list_resumes(session)
    result = []
    for r in rows:
        result.append({
            "id": r.id,
            "filename": r.filename,
            "name": r.name,
            "email": r.email,
            "phone": r.phone
        })
    return result

@app.get("/api/resumes/{resume_id}")
def get_resume(resume_id: int, session: Session = Depends(get_session)):
    try:
        r = crud.get_resume(session, resume_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {
        "id": r.id,
        "filename": r.filename,
        "uploaded_at": r.uploaded_at.isoformat(),
        "name": r.name,
        "email": r.email,
        "phone": r.phone,
        "extracted_data": json.loads(r.extracted_data) if r.extracted_data else None,
        "llm_analysis": json.loads(r.llm_analysis) if r.llm_analysis else None
    }
