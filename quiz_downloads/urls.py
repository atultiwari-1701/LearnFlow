from django.urls import path
from . import views

urlpatterns = [
    path('upload', views.store_quiz_download_files, name='store_quiz_download_files'),
]
