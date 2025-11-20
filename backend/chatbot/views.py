import os
import base64
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from mistralai import Mistral
from .models import ChatMessage


# API key
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')

# Initialize Mistral client
mistral_client = Mistral(api_key=MISTRAL_API_KEY)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    """
    Handle chatbot messages with minimax-m2:cloud model
    """
    message = request.data.get('message', '')

    if not message:
        return Response(
            {'error': 'Message is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Get chat context (last 5 messages)
        previous_messages = ChatMessage.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]

        # Build conversation history for context
        messages = []
        for prev_msg in reversed(list(previous_messages)):
            messages.append({'role': 'user', 'content': prev_msg.message})
            messages.append({'role': 'assistant', 'content': prev_msg.response})

        # Add system prompt
        system_prompt = """Вы - помощник по льготам и социальным выплатам для инвалидов в России.
Вы помогаете пользователям найти информацию о доступных льготах, пенсиях, технических средствах реабилитации и других мерах поддержки.
ВАЖНО: Отвечайте КРАТКО и ПО СУЩЕСТВУ. Максимум 2-3 предложения. Избегайте длинных объяснений.
Если вы не знаете ответа, честно скажите об этом и порекомендуйте обратиться в Социальный фонд России."""

        messages.insert(0, {'role': 'system', 'content': system_prompt})

        # Add current message
        messages.append({'role': 'user', 'content': message})

        # Call Mistral API for chat
        from mistralai.models import UserMessage, SystemMessage, AssistantMessage

        # Convert messages to Mistral format
        mistral_messages = []
        for msg in messages:
            if msg['role'] == 'system':
                mistral_messages.append(SystemMessage(content=msg['content']))
            elif msg['role'] == 'user':
                mistral_messages.append(UserMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                mistral_messages.append(AssistantMessage(content=msg['content']))

        chat_response = mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=mistral_messages,
            temperature=0.7,
            max_tokens=300  # Shorter responses
        )

        assistant_response = chat_response.choices[0].message.content

        # Save to database
        ChatMessage.objects.create(
            user=request.user,
            message=message,
            response=assistant_response
        )

        return Response({
            'response': assistant_response,
            'timestamp': ChatMessage.objects.filter(user=request.user).latest('created_at').created_at
        })

    except Exception as e:
        return Response(
            {'error': f'Error processing message: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_history(request):
    """
    Get chat history for the authenticated user
    """
    messages = ChatMessage.objects.filter(user=request.user).order_by('-created_at')[:50]

    history = []
    for msg in reversed(list(messages)):
        history.append({
            'id': msg.id,
            'message': msg.message,
            'response': msg.response,
            'timestamp': msg.created_at
        })

    return Response({'history': history})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def speech_to_text(request):
    """
    Convert speech to text - Uses browser Web Speech API
    This is a placeholder as Mistral doesn't have STT API yet
    """
    # Frontend should use Web Speech API directly
    # This endpoint is kept for compatibility
    return Response({
        'error': 'Please use browser Web Speech API for speech recognition',
        'text': ''
    }, status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def text_to_speech(request):
    """
    Convert text to speech - Uses browser Web Speech API
    This is a placeholder as Mistral doesn't have TTS API yet
    """
    # Frontend should use Web Speech API directly
    # This endpoint is kept for compatibility
    return Response({
        'error': 'Please use browser Web Speech API for text-to-speech',
        'audio': ''
    }, status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_history(request):
    """
    Clear chat history for the authenticated user
    """
    deleted_count = ChatMessage.objects.filter(user=request.user).delete()[0]

    return Response({
        'message': f'Deleted {deleted_count} messages',
        'count': deleted_count
    })
