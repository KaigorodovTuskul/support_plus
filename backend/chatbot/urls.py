from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat, name='chat'),
    path('chat/history/', views.chat_history, name='chat_history'),
    path('chat/clear/', views.clear_history, name='clear_history'),
    path('voice/stt/', views.speech_to_text, name='speech_to_text'),
    path('voice/tts/', views.text_to_speech, name='text_to_speech'),
]
