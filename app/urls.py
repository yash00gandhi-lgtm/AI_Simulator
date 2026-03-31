from django.urls import path

from .views import (
    signup_page,
    signup_api,
    upload_page,
    upload_resume,
    questions_page,
    generate_questions,
    submit_answer,
    result_page,
    get_result
)

urlpatterns = [

    # =========================
    # 🧑‍💻 SIGNUP
    # =========================
    path('signup/', signup_page),
    path('api/signup/', signup_api),

    # =========================
    # 📄 UPLOAD RESUME
    # =========================
    path('upload/', upload_page),
    path('api/upload/', upload_resume),

    # =========================
    # ❓ QUESTIONS
    # =========================
    path('questions/', questions_page),
    path('api/questions/', generate_questions),

    # =========================
    # ✍️ ANSWER
    # =========================
    path('api/answer/', submit_answer),

    # =========================
    # 📊 RESULT
    # =========================
    path('result/', result_page),
    path('api/result/', get_result),
]