from django.urls import path
from . import views

urlpatterns = [
    path('save-quiz-attempt', views.save_quiz_attempt, name='save_quiz_attempt'),
    path('quiz-history', views.get_quiz_history, name='get_quiz_history'),
]