from django.contrib import admin
from .models import User, Resume, Question, Answer


admin.site.register(User)
admin.site.register(Resume)

admin.site.register(Question)
admin.site.register(Answer)

