from django.urls import path
from . import views

urlpatterns = [
    path('search', views.search_gemini, name='search_gemini'),
    path('generate-quiz', views.generate_quiz, name='generate_quiz'),
    
    path('generate-topic-videos', views.generate_videos_for_topic, name='generate_topic_videos'),
    path('generate-topic-articles', views.generate_articles_for_topic, name='generate_topic_articles'),
    path('generate-topic-documentation', views.generate_documentation_for_topic, name='generate_topic_documentation'),
]