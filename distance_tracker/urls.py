from django.urls import path
from .views import record_distance

urlpatterns = [
    path('record_distance/', record_distance, name='record_distance'),
]
