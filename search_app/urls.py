from django.urls import path
from . import views

urlpatterns = [
    path('test', views.test, name='test'),
    path('search/', views.search_gemini, name='search_gemini'),  

]