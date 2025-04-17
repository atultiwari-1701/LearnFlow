from django.contrib import admin
from .models import QuizAttempt, QuestionAttempt

# Register your models here.
admin.site.register(QuizAttempt)
admin.site.register(QuestionAttempt)