from django.db import models

class Topic(models.Model):
    name = models.CharField(max_length=255, unique=True)
    content = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

class VideoResource(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='videos')
    subtopic = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255)
    url = models.URLField()
    duration = models.CharField(max_length=20)
    thumbnail = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['topic', 'subtopic']),
        ]
        unique_together = ['topic', 'subtopic', 'url']

    def __str__(self):
        return f"{self.title} - {self.topic.name}"

class ArticleResource(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='articles')
    subtopic = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255)
    url = models.URLField()
    read_time = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['topic', 'subtopic']),
        ]
        unique_together = ['topic', 'subtopic', 'url']

    def __str__(self):
        return f"{self.title} - {self.topic.name}"

class DocumentationResource(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='documentation')
    subtopic = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255)
    url = models.URLField()
    doc_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['topic', 'subtopic']),
        ]
        unique_together = ['topic', 'subtopic', 'url']

    def __str__(self):
        return f"{self.title} - {self.topic.name}"

class QuizQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    QUESTION_TYPES = [
        ('mcq', 'Multiple Choice'),
        ('true-false', 'True/False'),
        ('multiple-correct', 'Multiple Correct')
    ]
    
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
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