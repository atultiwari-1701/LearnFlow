from django.db import models

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