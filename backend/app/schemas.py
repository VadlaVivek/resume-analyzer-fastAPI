from pydantic import BaseModel
from typing import Optional, Any, Dict

class ResumeSummary(BaseModel):
    id: int
    filename: str
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]

class ResumeDetail(BaseModel):
    id: int
    filename: str
    uploaded_at: str
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    extracted_data: Optional[Dict[str, Any]]
    llm_analysis: Optional[Dict[str, Any]]
