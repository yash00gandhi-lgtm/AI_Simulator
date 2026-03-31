import pdfplumber
import os
import requests
import json
import re


def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception:
        text = ""
    return text


API_KEY = os.getenv("OPENROUTER_API_KEY")


def generate_questions_from_resume(text):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    print("API KEY:", API_KEY)  # 🔥 DEBUG

    prompt = "Generate 5 personalized interview questions based on this resume. Return ONLY JSON in this format: [{\"text\":\"question\"}] Resume: " + text

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            print("API ERROR:", response.text)
            return None

        result = response.json()
        content = result["choices"][0]["message"]["content"]

        try:
            questions = json.loads(content)
            if not isinstance(questions, list):
                raise ValueError
        except:
            match = re.search(r'\[.*?\]', content, re.DOTALL)
            if match:
                questions = json.loads(match.group())
            else:
                print("RAW CONTENT:", content)
                return None

        clean_questions = []
        for q in questions:
            if isinstance(q, dict) and "text" in q:
                clean_questions.append({"text": q["text"]})

        return clean_questions

    except Exception as e:
        print("QUESTION ERROR:", str(e))
        return None


def evaluate_answer(question, answer, resume_text):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    print("API KEY:", API_KEY)  # 🔥 DEBUG

    prompt = "Evaluate this answer and return JSON with score, strengths, weaknesses, feedback. Resume: " + resume_text + " Question: " + question + " Answer: " + answer

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            print("API ERROR:", response.text)
            return None

        result = response.json()
        content = result["choices"][0]["message"]["content"]

        match = re.search(r'\{.*\}', content, re.DOTALL)

        if match:
            parsed = json.loads(match.group())
        else:
            raise ValueError

        return {
            "score": int(parsed.get("score", 50)),
            "strengths": parsed.get("strengths", ""),
            "weaknesses": parsed.get("weaknesses", ""),
            "feedback": parsed.get("feedback", "")
        }

    except Exception as e:
        print("AI ERROR:", str(e))
        return {
            "score": 50,
            "strengths": "ok",
            "weaknesses": "improve",
            "feedback": "try again"
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

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    print("API KEY:", API_KEY)  # 🔥 DEBUG

    qa_text = ""
    for a in answers:
        qa_text += "Question: " + a.question.text + " Answer: " + a.answer + " Score: " + str(a.score)

    prompt = "Analyze interview and return JSON with strengths, weaknesses, summary, roadmap. Data: " + qa_text

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            print("API ERROR:", response.text)
            return None

        result = response.json()
        content = result["choices"][0]["message"]["content"]

        match = re.search(r'\{.*\}', content, re.DOTALL)

        return json.loads(match.group())

    except Exception as e:
        print("FEEDBACK ERROR:", str(e))
        return {
            "strengths": [],
            "weaknesses": [],
            "summary": "",
            "roadmap": []
        }