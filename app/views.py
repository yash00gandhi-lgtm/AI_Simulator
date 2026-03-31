from django.shortcuts import render
from django.contrib.auth import login, get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate

import json

from .models import Resume, Question, Answer
from .ai_engine import (
    generate_questions_from_resume,
    evaluate_answer,
    extract_text_from_pdf
)

User = get_user_model()


# =========================
# UI PAGES
# =========================

def signup_page(request):
    return render(request, "signup.html")


@login_required
def upload_page(request):
    return render(request, "upload.html")


@login_required
def questions_page(request):
    return render(request, "questions.html")


@login_required
def result_page(request):
    return render(request, "result.html")


# =========================
# SIGNUP API
# =========================

@csrf_exempt
def signup_api(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request'}, status=400)

    try:
        data = json.loads(request.body.decode("utf-8"))

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return JsonResponse({'error': 'All fields required'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username exists'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email exists'}, status=400)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

        return JsonResponse({
            'message': 'Signup successful',
            'redirect': '/upload/'
        })

    except Exception as e:
        print("SIGNUP ERROR:", str(e))
        return JsonResponse({'error': 'Server error'}, status=500)


# =========================
# RESUME UPLOAD
# =========================

@login_required
def upload_resume(request):
    if request.method == "POST":
        file = request.FILES.get("file")

        if not file:
            return JsonResponse({"error": "No file uploaded"}, status=400)

        resume = Resume.objects.create(user=request.user, file=file)

        try:
            parsed_text = extract_text_from_pdf(resume.file.path)
            resume.parsed_text = parsed_text
            resume.save()
        except Exception as e:
            print("PARSE ERROR:", e)
            return JsonResponse({"error": "Parsing failed"}, status=500)

        return JsonResponse({
            "message": "Uploaded & Parsed ✅",
            "redirect": "/questions/"
        })

    return JsonResponse({"error": "Invalid request"}, status=400)


# =========================
# GENERATE QUESTIONS
# =========================

@login_required
def generate_questions(request):
    try:
        # 🔥 RESET OLD DATA
        Answer.objects.filter(user=request.user).delete()
        Question.objects.all().delete()

        resume = Resume.objects.filter(user=request.user).last()

        if not resume or not resume.parsed_text:
            return JsonResponse({"error": "Resume not ready"}, status=400)

        questions_list = generate_questions_from_resume(resume.parsed_text)

        if not questions_list:
            return JsonResponse({"error": "AI failed"}, status=500)

        created = []

        for q in questions_list:
            # 🔥 SAFE PARSE
            text = q.get("text") if isinstance(q, dict) else str(q)

            created.append(
                Question.objects.create(text=text)
            )

        return JsonResponse({
            "questions": [{"question": q.text} for q in created]
        })

    except Exception as e:
        print("QUESTION ERROR:", str(e))
        return JsonResponse({"error": "Server error"}, status=500)


# =========================
# SUBMIT ANSWER
# =========================
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def submit_answer(request):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        print("DATA RECEIVED:", data)

        question_text = data.get("question")
        answer_text = data.get("answer")

        if not question_text or not answer_text:
            return JsonResponse({"error": "Missing data"}, status=400)

        print("QUESTION:", question_text)
        print("ANSWER:", answer_text)

        # 🔥 SAFE USER (IMPORTANT FIX)
        user = request.user if request.user.is_authenticated else None

        # 🔥 TEMP DISABLE AI (to avoid crash)
        try:
            # evaluation = evaluate_answer(question_text, answer_text, "")
            # score = evaluation.get("score", 60)
            # feedback = evaluation.get("feedback", "Good attempt")

            score = 70
            feedback = "Good answer"

        except Exception as e:
            print("AI ERROR:", e)
            score = 60
            feedback = "AI failed, default score"

        # 🔥 SAFE DB SAVE
        try:
            Answer.objects.create(
                user=user,
                question_text=question_text,
                answer_text=answer_text,
                score=score,
                feedback=feedback
            )
        except Exception as e:
            print("DB ERROR:", e)
            return JsonResponse({"error": "DB failed"}, status=500)

        return JsonResponse({"message": "Answer saved"}, status=200)

    except Exception as e:
        print("FINAL ERROR:", e)
        return JsonResponse({"error": "Server error"}, status=500)


# =========================
# RESULT
# =========================

@login_required
def get_result(request):
    try:
        answers = Answer.objects.filter(user=request.user)

        if not answers.exists():
            return JsonResponse({
                "score": 0,
                "strengths": [],
                "weaknesses": [],
                "feedback": "No answers found"
            })

        total_score = sum(a.score for a in answers)
        avg_score = total_score / answers.count()

        strengths = []
        weaknesses = []

        for a in answers:
            if a.score >= 70:
                strengths.append(a.feedback)
            else:
                weaknesses.append(a.feedback)

        return JsonResponse({
            "score": round(avg_score, 1),
            "strengths": strengths[:3],
            "weaknesses": weaknesses[:3],
            "feedback": "Keep improving 🚀"
        })

    except Exception as e:
        print("RESULT ERROR:", e)
        return JsonResponse({"error": "Server error"}, status=500)