from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Resume(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    uploaded_at: datetime
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    extracted_data: Optional[str] = None   # JSON stored as text
    llm_analysis: Optional[str] = None     # JSON stored as text
