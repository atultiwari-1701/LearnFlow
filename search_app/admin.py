from django.contrib import admin
from .models import Topic, QuizQuestion, QuizAttempt, QuestionAttempt

# Register your models here.
admin.site.register(Topic)
admin.site.register(QuestionAttempt)
admin.site.register(QuizQuestion)
admin.site.register(QuizAttempt)