from sqlmodel import Session, select
from .models import Resume
from datetime import datetime
import json

def create_resume(session: Session, filename: str, extracted_data: dict, llm_analysis: dict, name=None, email=None, phone=None):
    r = Resume(
        filename=filename,
        uploaded_at=datetime.utcnow(),
        name=name,
        email=email,
        phone=phone,
        extracted_data=json.dumps(extracted_data, ensure_ascii=False),
        llm_analysis=json.dumps(llm_analysis, ensure_ascii=False)
    )
    session.add(r)
    session.commit()
    session.refresh(r)
    return r

def list_resumes(session: Session):
    return session.exec(select(Resume).order_by(Resume.uploaded_at.desc())).all()

def get_resume(session: Session, resume_id: int):
    return session.exec(select(Resume).where(Resume.id == resume_id)).one()
