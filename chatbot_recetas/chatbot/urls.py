from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('chat_bot/', views.chat_bot_view, name='chat_bot'),
]