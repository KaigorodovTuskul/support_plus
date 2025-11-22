from rest_framework.views import APIView
from rest_framework.response import Response
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Поиск льгот и коммерческих предложений',
        operation_description='Поиск по естественному языку с использованием векторного поиска и LLM',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['query'],
            properties={
                'query': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='Поисковый запрос на естественном языке (например: "льготы для пенсионеров в Москве")'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description='Результаты поиска',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'query': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description='Распарсенный поисковый запрос',
                            properties={
                                'intent': openapi.Schema(type=openapi.TYPE_STRING),
                                'keywords': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
                                'filters': openapi.Schema(type=openapi.TYPE_OBJECT),
                            }
                        ),
                        'benefits': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'title': openapi.Schema(type=openapi.TYPE_STRING),
                                    'description': openapi.Schema(type=openapi.TYPE_STRING),
                                    'type': openapi.Schema(type=openapi.TYPE_STRING, enum=['benefit']),
                                    'benefit_type': openapi.Schema(type=openapi.TYPE_STRING),
                                    'similarity': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT),
                                }
                            )
                        ),
                        'offers': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'title': openapi.Schema(type=openapi.TYPE_STRING),
                                    'description': openapi.Schema(type=openapi.TYPE_STRING),
                                    'type': openapi.Schema(type=openapi.TYPE_STRING, enum=['commercial']),
                                    'partner': openapi.Schema(type=openapi.TYPE_STRING),
                                    'discount': openapi.Schema(type=openapi.TYPE_STRING),
                                    'similarity': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT),
                                }
                            )
                        ),
                        'total_benefits': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_offers': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            ),
            400: openapi.Response(description='Ошибка: не указан поисковый запрос'),
            401: openapi.Response(description='Не авторизован'),
        },
        tags=['Поиск']
    )
    def post(self, request):
        query_text = request.data.get('query', '').strip()
        if not query_text:
            return Response({'error': 'Query is required'}, status=400)

        # Get user region for personalization
        user_profile = getattr(request.user, 'userprofile', None)
        user_region = user_profile.region if user_profile else None

        # 1. Parse query
        parsed = query_parser.parse(query_text, user_region)

        # 2. Generate query embedding
        query_embedding = embedding_service.generate(f"query: {query_text}")

        # 3. Search in FAISS
        search_results = vector_store.search(
            query_embedding,
            filters=parsed['filters'],
            top_k=20
        )

        # 4. Fetch actual objects from SQLite
        search_ids = [sid for sid, _ in search_results]
        search_records = SearchIndex.objects.filter(id__in=search_ids)

        # Group by type
        benefits = []
        offers = []
        similarity_scores = {}

        for sid, sim in search_results:
            similarity_scores[sid] = sim

        for record in search_records:
            # Attach similarity score
            record.search_similarity = similarity_scores.get(record.id, 0)

            if record.content_type_name == 'benefit':
                benefits.append(record.content_object)
            elif record.content_type_name == 'commercial':
                offers.append(record.content_object)

        # 5. Serialize with type information
        return Response({
            'query': parsed,
            'benefits': [{
                'id': b.id,
                'title': b.title,
                'description': b.description,
                'type': 'benefit',
                'benefit_type': b.benefit_type,
                'similarity': similarity_scores.get(
                    SearchIndex.objects.get(
                        content_type=ContentType.objects.get_for_model(Benefit),
                        object_id=b.id
                    ).id, 0
                )
            } for b in benefits[:10]],
            'offers': [{
                'id': o.id,
                'title': o.title,
                'description': o.description,
                'type': 'commercial',
                'partner': o.partner_name,
                'discount': o.discount_description,
                'similarity': similarity_scores.get(
                    SearchIndex.objects.get(
                        content_type=ContentType.objects.get_for_model(CommercialOffer),
                        object_id=o.id
                    ).id, 0
                )
            } for o in offers[:10]],
            'total_benefits': len(benefits),
            'total_offers': len(offers)
        })


class MixedSearchResultsView(APIView):
    """Get full details of mixed search results"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Получить полные детали результатов поиска',
        operation_description='Возвращает полную информацию о выбранных льготах и предложениях по их ID',
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            description='Массив ID для получения деталей',
            items=openapi.Items(
                type=openapi.TYPE_OBJECT,
                required=['type', 'id'],
                properties={
                    'type': openapi.Schema(type=openapi.TYPE_STRING, enum=['benefit', 'commercial'], description='Тип объекта'),
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID объекта'),
                }
            )
        ),
        responses={
            200: openapi.Response(
                description='Массив детализированных объектов',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'type': openapi.Schema(type=openapi.TYPE_STRING, enum=['benefit', 'commercial']),
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'title': openapi.Schema(type=openapi.TYPE_STRING),
                            'description': openapi.Schema(type=openapi.TYPE_STRING),
                        },
                        discriminator=openapi.Discriminator(
                            property_name='type',
                            mapping={
                                'benefit': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'requirements': openapi.Schema(type=openapi.TYPE_STRING),
                                        'how_to_get': openapi.Schema(type=openapi.TYPE_STRING),
                                        'documents_needed': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
                                        'regions': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
                                        'categories': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
                                    }
                                ),
                                'commercial': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'discount_description': openapi.Schema(type=openapi.TYPE_STRING),
                                        'how_to_use': openapi.Schema(type=openapi.TYPE_STRING),
                                        'partner_name': openapi.Schema(type=openapi.TYPE_STRING),
                                        'regions': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
                                    }
                                )
                            }
                        )
                    )
                )
            ),
            404: openapi.Response(description='Объект не найден'),
            401: openapi.Response(description='Не авторизован'),
        },
        tags=['Поиск']
    )
    def post(self, request):
        """Accept list of mixed IDs and return full objects"""
        item_ids = request.data.get('items', [])  # [{'type': 'benefit', 'id': 123}, ...]

        results = []
        for item in item_ids:
            if item['type'] == 'benefit':
                obj = get_object_or_404(Benefit, id=item['id'])
                results.append({
                    'type': 'benefit',
                    'id': obj.id,
                    'title': obj.title,
                    'description': obj.description,
                    'requirements': obj.requirements,
                    'how_to_get': obj.how_to_get,
                    'documents_needed': obj.documents_needed,
                    'regions': [r.name for r in obj.regions.all()],
                    'categories': [c.name for c in obj.categories.all()],
                })
            elif item['type'] == 'commercial':
                obj = get_object_or_404(CommercialOffer, id=item['id'])
                results.append({
                    'type': 'commercial',
                    'id': obj.id,
                    'title': obj.title,
                    'description': obj.description,
                    'discount_description': obj.discount_description,
                    'how_to_use': obj.how_to_use,
                    'partner_name': obj.partner_name,
                    'regions': [r.name for r in obj.regions.all()],
                })

        return Response(results)