from django.urls import path
from .views import generate_analysis, upload_chunk

urlpatterns = [
    path('generate-analysis/', generate_analysis, name='generate_analysis'),
    path('upload_chunk/', upload_chunk, name='upload_chunk'),
]
