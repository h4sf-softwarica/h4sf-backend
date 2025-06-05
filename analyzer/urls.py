from django.urls import path
from .views import generate_analysis

urlpatterns = [
    path('generate-analysis/', generate_analysis, name='generate_analysis'),
]
