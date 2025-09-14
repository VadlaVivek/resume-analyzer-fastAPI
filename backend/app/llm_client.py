import os
import re
import json
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  

def debug_print(*args, **kwargs):
    print(*args, **kwargs, flush=True)

def quick_email(text):
    m = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return m.group(0) if m else None

def quick_phone(text):
    m = re.search(r'(\+?\d{1,3}[-\s]?)?(\(?\d{2,4}\)?[-\s]?)?\d{3,4}[-\s]?\d{3,4}', text)
    return m.group(0).strip() if m else None

def quick_name_from_text(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for ln in lines[:5]:
        if '@' not in ln and len(ln.split()) <= 4 and not re.search(r'\d', ln):
            return ln
    return None

def call_gemini(prompt: str) -> str:
    """
    Call Gemini via google.generativeai if available.
    If the SDK/import fails, this raises and will trigger fallback to heuristics.
    """
    try:
        import google.generativeai as genai  
    except Exception as e:
        raise RuntimeError(f"Gemini SDK not available: {e}")

    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set in environment")

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-pro")
    resp = model.generate_content(prompt)
    if hasattr(resp, "text"):
        return resp.text
    return str(resp)


def remove_markdown_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*```$', '', text)
    return text.strip()

def force_brace_wrap(text: str) -> str:
    """
    If text is key-value lines without surrounding braces, try to wrap them.
    Also make sure we only keep from first '{' to last '}' if present.
    """
    t = text.strip()
    t = remove_markdown_fences(t)

    if '{' in t and '}' in t:
        start = t.find('{')
        end = t.rfind('}') + 1
        candidate = t[start:end]
        return candidate.strip()

    if re.match(r'^[\s\n]*["\']?\w+["\']?\s*:', t):
        t_wrapped = '{' + t + '}'
        return t_wrapped

    return t

def try_json_loads(text: str):
    """
    Try several strategies to parse text into JSON. Returns dict or raises.
    """
    try:
        return json.loads(text)
    except Exception:
        pass

    cleaned = remove_markdown_fences(text)
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    forced = force_brace_wrap(text)
    try:
        return json.loads(forced)
    except Exception:
        pass

    keys = ["name", "email", "phone", "core_skills", "soft_skills", "work_experience", "education", "summary"]
    result = {}
    for k in keys:
        m = re.search(rf'"?{k}"?\s*:\s*(\[[^\]]*\]|\{{[^\}}]*\}}|"(?:[^"\\]|\\.)*"|[^\n,]+)', text, flags=re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            if val.startswith('[') or val.startswith('{'):
                try:
                    result[k] = json.loads(val)
                except Exception:
                    items = re.findall(r'["\']([^"\']+)["\']|([^,\[\]]+)', val)
                    arr = []
                    for a,b in items:
                        arr.append((a or b).strip())
                    result[k] = [x for x in arr if x]
            else:
                if val.startswith('"') and val.endswith('"'):
                    result[k] = val[1:-1]
                else:
                    result[k] = val.rstrip(',').strip()
    if result:
        return result

    raise ValueError("Could not parse JSON from LLM output")


def heuristic_extract_from_resume_text(resume_text: str) -> dict:
    """
    Deterministic, regex-based extraction from the raw resume text.
    Works well for basic fields and is safe for demos if LLM fails.
    """
    rt = resume_text or ""
    name = quick_name_from_text(rt)
    email = quick_email(rt)
    phone = quick_phone(rt)

    core_skills = []
    m = re.search(r'(core skills|technical skills|skills)[:\-\n]+([^\n\r]+)', rt, flags=re.IGNORECASE)
    if m:
        skills_line = m.group(2)
        parts = re.split(r'[,\u2022\-\n]+', skills_line)
        core_skills = [p.strip() for p in parts if p.strip()]

    if not core_skills:
        tech_patterns = ["Python","JavaScript","React","Node","Django","Flask","SQL","Postgres","Mongo","AWS","Docker","Kubernetes","Java","C++","TypeScript"]
        found = []
        for pat in tech_patterns:
            if re.search(r'\b' + re.escape(pat) + r'\b', rt, flags=re.IGNORECASE):
                found.append(pat)
        core_skills = found

    work_experience = []
    mexp = re.search(r'(experience|work experience|professional experience)[:\n\r]+(.+?)(?:\n\n|\neducation|\n$)', rt, flags=re.IGNORECASE | re.DOTALL)
    if mexp:
        block = mexp.group(2).strip()
        lines = [l.strip(" -•\t") for l in block.splitlines() if l.strip()]
        
        for ln in lines[:6]:
            mm = re.match(r'(?P<title>.+?)\s+at\s+(?P<company>.+?)(?:\s+\(|$)', ln, flags=re.IGNORECASE)
            if mm:
                work_experience.append({"title": mm.group("title").strip(), "company": mm.group("company").strip(), "description": ln})
            else:
                work_experience.append({"title": ln, "company": "", "description": ln})

    # Education
    education = []
    medit = re.search(r'(education)[:\n\r]+(.+?)(?:\n\n|\nexperience|\n$)', rt, flags=re.IGNORECASE | re.DOTALL)
    if medit:
        block = medit.group(2).strip()
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        for ln in lines[:5]:
            parts = [p.strip() for p in re.split(r',|-', ln) if p.strip()]
            education.append({"degree": parts[0] if parts else ln, "institution": parts[1] if len(parts)>1 else "", "year": parts[-1] if parts and re.search(r'\d{4}', parts[-1]) else ""})

    summary = None
    lines = [l.strip() for l in rt.splitlines() if l.strip()]
    if len(lines) > 1:
        summary = lines[1]
    result = {
        "name": name,
        "email": email,
        "phone": phone,
        "core_skills": core_skills,
        "soft_skills": [],
        "work_experience": work_experience,
        "education": education,
        "summary": summary or ""
    }
    return result


def heuristic_analyze(structured: dict) -> dict:
    score = 4
    skills = structured.get("core_skills") or []
    exp = structured.get("work_experience") or []
    edu = structured.get("education") or []
    summary = structured.get("summary") or ""

    if summary and len(summary) > 30:
        score += 1
    if len(skills) >= 3:
        score += 2
    elif len(skills) >= 1:
        score += 1
    if len(exp) >= 1:
        score += 2
    if len(edu) >= 1:
        score += 1

    score = max(1, min(10, score))

    improvements = []
    if not structured.get("email") or not structured.get("phone"):
        improvements.append("Add clear contact information (email & phone) at the top.")
    if len(exp) == 0:
        improvements.append("Add at least one work experience entry with dates and measurable results.")
    else:
        has_metric = any(re.search(r'\d+%', (we.get("description") or "")) or re.search(r'\d+', (we.get("description") or "")) for we in exp)
        if not has_metric:
            improvements.append("Quantify achievements in work experience (use numbers/metrics).")
    if len(skills) < 3:
        improvements.append("List more technical skills and specify proficiency where possible.")
    if not improvements:
        improvements.append("Resume is fine; consider formatting and concise bullets.")

    suggestions = []
    needed = ["Docker", "SQL", "AWS", "TypeScript", "Git"]
    present = [s.lower() for s in skills]
    for s in needed:
        if s.lower() not in present and len(suggestions) < 3:
            suggestions.append({"skill": s, "why": f"Commonly required for modern full-stack roles ({s})."})

    return {
        "resume_rating": score,
        "improvement_areas": " ".join(improvements),
        "upskill_suggestions": suggestions
    }


EXTRACTION_PROMPT = """
You are an expert HR recruiter.
Return ONLY valid JSON. 
The response MUST start with '{' and end with '}'.
Do not include explanations, notes, or markdown formatting.

JSON schema:
{
  "name": "string | null", 
"email": "string | null", 
"phone": "string | null", 
"linkedin_url": "string | null", 
"portfolio_url": "string | null", 
"summary": "string | null", 

"education": [{ "degree": "string", "institution": "string", "graduation_year": "string" }], 
"technical_skills": ["string"], 
"soft_skills": ["string"], 
"resume_rating": "number (1-10)", 
"improvement_areas": "string", 
"upskill_suggestions": ["string"] 
}

Resume text:
\"\"\"{resume_text}\"\"\"
"""

ANALYSIS_PROMPT = """
You are a career coach. 
Based on the provided resume data in JSON format, 
provide a critical analysis. Return a JSON object with three keys: resume_rating (a 
score from 1 to 10), improvement_areas (a paragraph with actionable advice), and 
upskill_suggestions (a list of 3-5 relevant skills to learn, with a brief explanation for 
each)

Resume JSON:
{resume_json}
"""



def extract_structured_data(resume_text: str) -> dict:
    try:
        raw = call_gemini(EXTRACTION_PROMPT.format(resume_text=resume_text))
        debug_print("=== GEMINI RAW EXTRACTION OUTPUT ===")
        debug_print(raw)
        parsed = try_json_loads(raw)
        parsed["_llm_raw"] = raw  
        parsed["_source"] = "llm"
        return parsed
    except Exception as e:
        debug_print("LLM extraction failed, falling back to heuristic extractor. Error:", e)
        heur = heuristic_extract_from_resume_text(resume_text)
        heur["_llm_error"] = str(e)
        heur["_source"] = "heuristic"
        return heur

def analyze_resume(structured_json: dict) -> dict:
    try:
        raw = call_gemini(ANALYSIS_PROMPT.format(resume_json=json.dumps(structured_json)))
        debug_print("=== GEMINI RAW ANALYSIS OUTPUT ===")
        debug_print(raw)
        parsed = try_json_loads(raw)
        parsed["_llm_raw"] = raw
        parsed["_source"] = "llm"
        return parsed
    except Exception as e:
        debug_print("LLM analysis failed, falling back to heuristic analyzer. Error:", e)
        heur = heuristic_analyze(structured_json)
        heur["_llm_error"] = str(e)
        heur["_source"] = "heuristic"
        return heur
