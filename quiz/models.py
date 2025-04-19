from django.db import models
from authentication.models import User
from search_app.models import QuizQuestion, Topic
from django.utils import timezone

# Create your models here.
class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_time_taken = models.IntegerField(help_text="Total time taken in seconds")
    score = models.IntegerField()
    correct_attempts = models.IntegerField()
    incorrect_attempts = models.IntegerField()
    partial_attempts = models.IntegerField()
    unattempted = models.IntegerField()
    is_negative_marking = models.BooleanField(default=False, help_text="Whether negative marking was enabled for this quiz")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='quiz_attempts')
    subtopic = models.CharField(max_length=255, help_text="Subtopic of the quiz", blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['topic']),
        ]

    def __str__(self):
        return f"{self.user.name}'s attempt on {self.topic.name} - {self.subtopic} at {self.created_at}"

    @property
    def total_questions(self):
        """Calculate total number of questions in the quiz"""
        return self.correct_attempts + self.incorrect_attempts + self.partial_attempts + self.unattempted

    @property
    def total_possible_score(self):
        """Calculate maximum possible score (4 points per question)"""
        return self.total_questions * 4

    @property
    def score_percentage(self):
        """Calculate percentage score achieved"""
        if self.total_possible_score == 0 or self.score < 0:
            return 0
        return round((self.score / self.total_possible_score) * 100, 2)

class QuestionAttempt(models.Model):
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='question_attempts')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    time_taken = models.IntegerField(help_text="Time taken for this question in seconds")
    attempted_options = models.JSONField(help_text="Options selected by the user")

    @property
    def is_correct(self):
        """Check if the attempt is completely correct"""
        if not self.attempted_options:
            return False
        
        if self.question.question_type == 'multiple-correct':
            # For multiple correct, all correct options must be selected and no incorrect options
            correct_options = set(self.question.correct_answers)
            attempted = set(self.attempted_options)
            return correct_options == attempted
        else:
            # For MCQ and True/False, check if the selected option matches the correct answer
            return self.attempted_options == self.question.correct_answers

    @property
    def is_partial(self):
        """Check if the attempt is partially correct (only for multiple correct type)"""
        if self.question.question_type != 'multiple-correct' or not self.attempted_options:
            return False
        
        correct_options = set(self.question.correct_answers)
        attempted = set(self.attempted_options)
        
        # Check if at least one correct option is selected and no incorrect options
        return bool(correct_options.intersection(attempted)) and not (attempted - correct_options)

    @property
    def score(self):
        """Calculate score for this question attempt based on question type and negative marking"""
        if not self.attempted_options:
            return 0

        if self.question.question_type == 'multiple-correct':
            correct_options = set(self.question.correct_answers)
            attempted = set(self.attempted_options)
            
            # Check for incorrect selections
            incorrect_selections = len(attempted - correct_options)
            
            # If any incorrect option is selected, return -2
            if self.quiz_attempt.is_negative_marking and incorrect_selections > 0:
                return -2
            
            # Count correct selections
            correct_selections = len(correct_options.intersection(attempted))
            
            # If all correct options are selected, return 4
            if correct_selections == len(correct_options):
                return 4
            
            # Otherwise, return 1 point per correct option
            return correct_selections
        else:
            # For MCQ and True/False
            if self.is_correct:
                return 4
            elif self.quiz_attempt.is_negative_marking:
                return -1  # -1 mark for incorrect answer
            return 0

    def __str__(self):
        return f"Attempt for question {self.question.id} in quiz attempt {self.quiz_attempt.id}"