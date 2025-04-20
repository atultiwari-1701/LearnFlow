from django.urls import path
from . import views

urlpatterns = [
    path('search', views.search_gemini, name='search_gemini'),
    path('generate-resources', views.generate_resources, name='generate_resources'),
    path('generate-youtube-videos', views.generate_youtube_videos, name='generate_youtube_videos'),
    path('generate-quiz', views.generate_quiz, name='generate_quiz'),
    path('test', views.test, name='test'),
    path('generate-topic-resources', views.generate_resources_for_topic, name='generate_resources_for_topic'),
    # New URLs for separate resource generation
    path('generate-topic-videos', views.generate_videos_for_topic, name='generate_topic_videos'),
    path('generate-topic-articles', views.generate_articles_for_topic, name='generate_topic_articles'),
    path('generate-topic-documentation', views.generate_documentation_for_topic, name='generate_topic_documentation'),
]