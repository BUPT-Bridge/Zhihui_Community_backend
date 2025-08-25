from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('insert-text/', views.insert_text_with_auth, name='insert_text_with_auth'),
    path('search-text/', views.search_text_with_auth, name='search_text_with_auth'),
    path('export-csv/', views.export_to_csv, name='export_to_csv'),
]
