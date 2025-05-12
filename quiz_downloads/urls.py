from django.urls import path
from . import views

urlpatterns = [
    path('get-quiz-download-url', views.get_quiz_download_presigned_url, name='get_quiz_download_presigned_url'),
    path('upload', views.store_quiz_download_files, name='store_quiz_download_files'),
]
