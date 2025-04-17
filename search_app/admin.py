from django.contrib import admin
from .models import Topic, QuizQuestion

# Register your models here.
admin.site.register(Topic)

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'question_type')