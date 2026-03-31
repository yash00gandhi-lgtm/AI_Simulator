from django.db import models
from django.contrib.auth.models import AbstractUser


# =========================
# USER
# =========================
class User(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.email


# =========================
# RESUME
# =========================
class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/')
    parsed_text = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.email}"


# =========================
# QUESTION
# =========================
class Question(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text[:50]


# =========================
# ANSWER (SIMPLIFIED 🔥)
# =========================
class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


    question_text = models.TextField()
    answer_text = models.TextField()

    score = models.IntegerField(default=0)
    feedback = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.score}"