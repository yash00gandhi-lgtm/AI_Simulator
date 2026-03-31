import pdfplumber

import requests

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception:
        text = ""
    return text




API_KEY = "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"

def generate_questions_from_resume(text):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are an expert interviewer.

Analyze the resume carefully and generate 5 UNIQUE, non-generic interview questions.

Rules:
- Questions MUST be based on skills, projects, or experience in the resume
- Avoid common questions like "Tell me about yourself"
- Make questions specific and personalized
- Each question should be different every time

Return ONLY JSON:
[
  {{"text": "question 1"}},
  {{"text": "question 2"}},
  {{"text": "question 3"}},
  {{"text": "question 4"}},
  {{"text": "question 5"}}
]

Resume:
{text}
"""

    data = {
        "model": "openai/gpt-4o-mini",   # 🔥 FIXED MODEL
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.9
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        # 🔥 STATUS CHECK
        if response.status_code != 200:
            print("API ERROR:", response.text)
            return None

        result = response.json()

        content = result["choices"][0]["message"]["content"]

        import json, re

        # 🔥 SAFE JSON EXTRACTION
        match = re.search(r'\[.*\]', content, re.DOTALL)

        if match:
            questions = json.loads(match.group())
        else:
            raise ValueError("Invalid JSON")

        return questions

    except Exception as e:
        print("❌ QUESTION GEN ERROR:", str(e))
        return None



OPENROUTER_API_KEY = "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"

def evaluate_answer(question, answer, resume_text):
    import requests, json, re

    url = "https://openrouter.ai/api/v1/chat/completions"

    prompt = f"""
You are a strict technical interviewer.

Evaluate the candidate's answer.

⚠️ IMPORTANT:
- Return ONLY valid JSON
- Do NOT add any text before or after JSON
- Score must be between 0 and 100

FORMAT:

{{
  "score": 75,
  "strengths": "clear explanation",
  "weaknesses": "lacks depth",
  "feedback": "good but can improve"
}}

Resume:
{resume_text}

Question:
{question}

Answer:
{answer}
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        content = result["choices"][0]["message"]["content"]

        print("🧠 RAW AI RESPONSE:", content)

        # 🔥 SAFE JSON EXTRACTION
        match = re.search(r'\{.*\}', content, re.DOTALL)

        if match:
            parsed = json.loads(match.group())
        else:
            raise ValueError("No JSON found")

        # 🔥 SAFETY DEFAULTS
        return {
            "score": int(parsed.get("score", 50)),
            "strengths": parsed.get("strengths", "Good attempt"),
            "weaknesses": parsed.get("weaknesses", "Needs improvement"),
            "feedback": parsed.get("feedback", "Decent answer")
        }

    except Exception as e:
        print("❌ AI ERROR:", str(e))

        # 🔥 FALLBACK (VERY IMPORTANT)
        return {
            "score": 50,
            "strengths": "Answer submitted",
            "weaknesses": "AI parsing issue",
            "feedback": "Try again"
        }
def generate_result_summary(answers):

    total_score = sum([a.score for a in answers])
    avg_score = total_score / len(answers) if answers else 0

    ai_data = generate_ai_feedback(answers)

    return {
        "total_score": total_score,
        "avg_score": round(avg_score, 1),
        "strengths": ai_data.get("strengths", []),
        "weaknesses": ai_data.get("weaknesses", []),
        "summary": ai_data.get("summary", ""),
        "roadmap": ai_data.get("roadmap", [])
    }

def generate_ai_feedback(answers):

    import requests, json, re

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # 🔥 Build Q/A text
    qa_text = ""
    for a in answers:
        qa_text += f"""
Question: {a.question.text}
Answer: {a.answer}
Score: {a.score}
"""

    prompt = f"""
You are an expert interview coach.

Analyze the interview and give:
- strengths
- weaknesses
- short summary
- improvement roadmap

Return ONLY JSON:
{{
  "strengths": [],
  "weaknesses": [],
  "summary": "",
  "roadmap": []
}}

Data:
{qa_text}
"""

    data = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        result = response.json()
        content = result["choices"][0]["message"]["content"]

        match = re.search(r'\{.*\}', content, re.DOTALL)

        return json.loads(match.group())

    except Exception as e:
        print("AI FEEDBACK ERROR:", e)
        return {
            "strengths": [],
            "weaknesses": [],
            "summary": "Could not generate AI feedback",
            "roadmap": []
        }