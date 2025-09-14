## Resume Analyzer ##

* This project is a Full-Stack Resume Analyzer built with:
- Backend: FastAPI (Python), PostgreSQL/SQLite, Gemini API (LLM)
- Frontend: React + Axios
- Database: SQLAlchemy ORM

It extracts key fields from resumes (PDFs), analyzes them, and provides ratings + improvement suggestions.

* Features
- Upload a PDF resume
- Extract contact info, skills, experience, education
- Analyze resume quality using LLM + heuristic fallback
- Store results in database
- View extracted + analyzed JSON in UI


# Backend Setup (FastAPI)

1. Open a terminal inside the backend folder:
2. Create & activate virtual environment:

   // python -m venv .venv
   // .venv\Scripts\activate    # (Windows)

3. Install dependencies:
   // pip install -r requirements.txt

4. Create a .env file inside backend/ with your Gemini API key:
   // GEMINI_API_KEY=your_api_key_here

5. Run the backend server:
   // uvicorn app.main:app --reload --port 8000


# Frontend Setup (React)

1. Open a new terminal inside frontend folder:

2. Install dependencies:
   // npm install

3. Start React app:
   // npm start

* The UI runs at: http://localhost:3000