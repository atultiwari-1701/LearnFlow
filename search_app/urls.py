from django.urls import path
from . import views

urlpatterns = [
    path('test', views.test, name='test'),
    path('search', views.search_gemini, name='search_gemini'),
    path('generate-resources', views.generate_resources, name='generate_resources'), 
    path('generate-youtube-videos', views.generate_youtube_videos, name='generate_youtube_videos'),
    path('generate-quiz', views.generate_quiz, name='generate_quiz'),
    path('save-quiz-attempt', views.save_quiz_attempt, name='save_quiz_attempt'),
]