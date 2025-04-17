from django.db import models
from authentication.models import User
from search_app.models import QuizQuestion
from django.utils import timezone

# Create your models here.
class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    total_time_taken = models.IntegerField(help_text="Total time taken in seconds")
    score = models.IntegerField(help_text="Total score achieved")
    correct_attempts = models.IntegerField(help_text="Number of correctly attempted questions")
    incorrect_attempts = models.IntegerField(help_text="Number of incorrectly attempted questions")
    partial_attempts = models.IntegerField(help_text="Number of partially correct attempts")
    unattempted = models.IntegerField(help_text="Number of unattempted questions")

    class Meta:
        ordering = ['-created_at']  # Order by most recent first
        indexes = [
            models.Index(fields=['user_id']),  # Add index for user_id
        ]

    def __str__(self):
        return f"Quiz Attempt by {self.user.name} on {self.created_at}"

class QuestionAttempt(models.Model):
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='question_attempts')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    time_taken = models.IntegerField(help_text="Time taken for this question in seconds")
    attempted_options = models.JSONField(help_text="List of options selected by the user")

    def __str__(self):
        return f"Question Attempt for {self.question.id} in Quiz {self.quiz_attempt.id}"

    @property
    def is_correct(self):
        """Calculate if the attempt was completely correct"""
        attempted_options = set(self.attempted_options)
        correct_answers = set(self.question.correct_answers)
        return attempted_options == correct_answers

    @property
    def is_partial(self):
        """Calculate if the attempt was partially correct"""
        attempted_options = set(self.attempted_options)
        correct_answers = set(self.question.correct_answers)
        return (
            len(attempted_options.intersection(correct_answers)) > 0 and
            len(attempted_options - correct_answers) == 0
        )