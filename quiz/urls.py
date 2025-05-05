from django.urls import path
from . import views

urlpatterns = [
    path('save-quiz-attempt', views.save_quiz_attempt, name='save_quiz_attempt'),
    path('topics', views.get_topics_paginated, name='get_topics_paginated'),
    path('quizzes-for-topic/<int:topic_id>', views.get_quizzes_for_topic, name='get_quizzes_for_topic'),
    path('questions-for-quiz/<int:quiz_attempt_id>', views.get_questions_for_quiz_attempt, name='get_questions_for_quiz_attempt'),
    path('quiz-stats', views.get_quiz_stats, name='get_quiz_stats'),
]