from django.urls import path
from . import views

urlpatterns = [
    path('api/search/', views.NaturalLanguageSearchAPI.as_view(), name='natural-search'),
    path('api/search/details/', views.MixedSearchResultsView.as_view(), name='search-details'),

    # Pages
    path('', views.DocumentListView.as_view(), name='document-list'),
    path('personal/', views.PersonalPageView.as_view(), name='personal-page'),
]