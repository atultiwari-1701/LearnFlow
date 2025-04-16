from django.db import models
from django.utils import timezone
from authentication.models import User

class Topic(models.Model):
    name = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return self.name

class QuizQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    QUESTION_TYPES = [
        ('mcq', 'Multiple Choice'),
        ('true-false', 'True/False'),
        ('multiple-correct', 'Multiple Correct')
    ]
    
    topic = models.CharField(max_length=255)
    subtopic = models.CharField(max_length=255, blank=True)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    question = models.TextField(unique=True)
    options = models.JSONField()  # Store as JSON array
    correct_answers = models.JSONField()  # Store as JSON array
    explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=20, choices=[('gemini', 'Gemini'), ('manual', 'Manual')], default='gemini')

    class Meta:
        indexes = [
            models.Index(fields=['topic', 'subtopic', 'question_type']),
        ]

    def __str__(self):
        return f"{self.question[:50]}..."

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

    def __str__(self):
        return f"Quiz Attempt by {self.user.username} on {self.created_at}"

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