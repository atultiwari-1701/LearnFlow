from django.contrib import admin
from .models import QuizAttempt, QuestionAttempt

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'score', 'total_questions', 'total_possible_score', 'score_percentage', 'is_negative_marking')
    readonly_fields = ('total_questions', 'total_possible_score', 'score_percentage')

@admin.register(QuestionAttempt)
class QuestionAttemptAdmin(admin.ModelAdmin):
    list_display = ('quiz_attempt', 'question', 'time_taken', 'is_correct', 'is_partial', 'score')
    readonly_fields = ('is_correct', 'is_partial', 'score')