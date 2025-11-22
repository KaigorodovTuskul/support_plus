import os
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from mistralai import Mistral
from .models import ChatMessage
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Search integration
from search.embedding_service import LocalEmbeddingService
from search.vector_store import InMemoryVectorStore
from search.models import SearchIndex
from benefits.models import Benefit, CommercialOffer
from django.contrib.contenttypes.models import ContentType

# API key
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')

# Initialize Mistral client
mistral_client = Mistral(api_key=MISTRAL_API_KEY)

# Initialize search services
embedding_service = LocalEmbeddingService()
vector_store = InMemoryVectorStore()


@swagger_auto_schema(
    method='post',
    operation_summary='Чат с ИИ-ассистентом',
    operation_description='Отправляет сообщение ИИ-ассистенту и получает ответ с учетом истории разговора',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['message'],
        properties={
            'message': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Текст сообщения пользователя',
                example='Какие льготы доступны для инвалидов 1 группы?'
            )
        }
    ),
    responses={
        200: openapi.Response(
            description='Ответ от ИИ-ассистента',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'response': openapi.Schema(type=openapi.TYPE_STRING, description='Текст ответа от ИИ'),
                    'timestamp': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Время создания сообщения'),
                }
            )
        ),
        400: openapi.Response(description='Сообщение не предоставлено'),
        500: openapi.Response(description='Ошибка обработки сообщения'),
        401: openapi.Response(description='Не авторизован'),
    },
    tags=['Чат-бот']
)
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
        # 1. Search for relevant context
        context_text = ""
        try:
            # Generate embedding
            query_embedding = embedding_service.generate(f"query: {message}")
            
            # Search in vector store
            search_results = vector_store.search(
                query_embedding,
                filters={}, # No filters for now, search everything
                top_k=3
            )
            
            if search_results:
                search_ids = [sid for sid, _ in search_results]
                search_records = SearchIndex.objects.filter(id__in=search_ids)
                
                found_items = []
                for record in search_records:
                    if record.content_type_name == 'benefit':
                        try:
                            benefit = Benefit.objects.get(id=record.object_id)
                            found_items.append(f"Льгота: {benefit.title}\nОписание: {benefit.description}\nКто может получить: {benefit.requirements}")
                        except Benefit.DoesNotExist:
                            continue
                    elif record.content_type_name == 'commercial':
                        try:
                            offer = CommercialOffer.objects.get(id=record.object_id)
                            found_items.append(f"Предложение: {offer.title}\nПартнер: {offer.partner_name}\nСкидка: {offer.discount_description}")
                        except CommercialOffer.DoesNotExist:
                            continue
                
                if found_items:
                    context_text = "\n\nНАЙДЕННАЯ ИНФОРМАЦИЯ ИЗ БАЗЫ ДАННЫХ:\n" + "\n---\n".join(found_items)
                    print(f"Found {len(found_items)} relevant items for context")
        except Exception as e:
            print(f"Error retrieving context: {e}")
            # Continue without context if search fails

        # Get chat context (last 5 messages)
        previous_messages = ChatMessage.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]

        # Build conversation history for context
        messages = []
        for prev_msg in reversed(list(previous_messages)):
            messages.append({'role': 'user', 'content': prev_msg.message})
            messages.append({'role': 'assistant', 'content': prev_msg.response})

        # Add system prompt with context
        system_prompt = """Вы - помощник по льготам и социальным выплатам для инвалидов в России.
Вы помогаете пользователям найти информацию о доступных льготах, пенсиях, технических средствах реабилитации и других мерах поддержки.
ВАЖНО: Отвечайте КРАТКО и ПО СУЩЕСТВУ. Максимум 2-3 предложения. Избегайте длинных объяснений.
Если вы не знаете ответа, честно скажите об этом и порекомендуйте обратиться в Социальный фонд России.

ИНСТРУКЦИЯ ПО ПОИСКУ:
Если пользователь явно просит найти льготы, показать список льгот, или спрашивает "какие льготы есть для...", вы должны добавить в конец ответа специальный тег: [SEARCH: поисковый запрос].
Пример: Пользователь спрашивает "Какие льготы на проезд?". Вы отвечаете: "Вам могут быть доступны льготы на бесплатный проезд в общественном транспорте. [SEARCH: льготы на проезд]"."""

        if context_text:
            system_prompt += f"\n\nИспользуйте следующую информацию для ответа на вопрос пользователя, если она релевантна:{context_text}"

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
        
        # Parse for search intent
        search_query = None
        if '[SEARCH:' in assistant_response:
            try:
                start_idx = assistant_response.find('[SEARCH:')
                end_idx = assistant_response.find(']', start_idx)
                if end_idx != -1:
                    search_tag = assistant_response[start_idx:end_idx+1]
                    search_query = search_tag.replace('[SEARCH:', '').replace(']', '').strip()
                    # Remove the tag from the visible response
                    assistant_response = assistant_response.replace(search_tag, '').strip()
            except Exception as e:
                print(f"Error parsing search tag: {e}")

        # Save to database
        ChatMessage.objects.create(
            user=request.user,
            message=message,
            response=assistant_response
        )

        response_data = {
            'response': assistant_response,
            'timestamp': ChatMessage.objects.filter(user=request.user).latest('created_at').created_at
        }
        
        if search_query:
            response_data['search_query'] = search_query

        return Response(response_data)

    except Exception as e:
        return Response(
            {'error': f'Error processing message: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='get',
    operation_summary='Получить историю чата',
    operation_description='Возвращает последние 50 сообщений пользователя в хронологическом порядке',
    responses={
        200: openapi.Response(
            description='История чата',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'history': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID сообщения'),
                                'message': openapi.Schema(type=openapi.TYPE_STRING, description='Сообщение пользователя'),
                                'response': openapi.Schema(type=openapi.TYPE_STRING, description='Ответ ИИ'),
                                'timestamp': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Время сообщения'),
                            }
                        )
                    )
                }
            )
        ),
        401: openapi.Response(description='Не авторизован'),
    },
    tags=['Чат-бот']
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


@swagger_auto_schema(
    method='post',
    operation_summary='Речь в текст (заглушка)',
    operation_description='Текущая реализация использует браузерный Web Speech API. Этот эндпоинт оставлен для совместимости.',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'audio': openapi.Schema(type=openapi.TYPE_STRING, format='binary', description='Аудио данные (не используется)'),
        }
    ),
    responses={
        501: openapi.Response(
            description='Не реализовано',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING),
                    'text': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
    },
    tags=['Чат-бот']
)
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


@swagger_auto_schema(
    method='post',
    operation_summary='Текст в речь (заглушка)',
    operation_description='Текущая реализация использует браузерный Web Speech API. Этот эндпоинт оставлен для совместимости.',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'text': openapi.Schema(type=openapi.TYPE_STRING, description='Текст для преобразования (не используется)'),
        }
    ),
    responses={
        501: openapi.Response(
            description='Не реализовано',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING),
                    'audio': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
    },
    tags=['Чат-бот']
)
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


@swagger_auto_schema(
    method='delete',
    operation_summary='Очистить историю чата',
    operation_description='Удаляет всю историю сообщений текущего пользователя',
    responses={
        200: openapi.Response(
            description='История очищена',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Сообщение об успехе'),
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Количество удаленных сообщений'),
                }
            )
        ),
        401: openapi.Response(description='Не авторизован'),
    },
    tags=['Чат-бот']
)
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