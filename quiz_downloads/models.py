from django.db import models
from quiz.models import QuizAttempt

# Create your models here.
class QuizDownload(models.Model):
    quiz_attempt = models.OneToOneField(QuizAttempt, on_delete=models.CASCADE, related_name='download')
    questions_txt = models.CharField(max_length=255, blank=True, null=True)
    questions_pdf = models.CharField(max_length=255, blank=True, null=True)
    answers_txt = models.CharField(max_length=255, blank=True, null=True)
    answers_pdf = models.CharField(max_length=255, blank=True, null=True)
    user_attempt_txt = models.CharField(max_length=255, blank=True, null=True)
    user_attempt_pdf = models.CharField(max_length=255, blank=True, null=True)
    report_pdf = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    storage_index = models.IntegerField(default=0, help_text="Index of the file in storage")

    def __str__(self):
        return f"Download for attempt {self.quiz_attempt}"