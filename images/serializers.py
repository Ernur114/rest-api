from rest_framework import serializers
from .models import Image

class ImageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Image.
    """
    class Meta:
        model = Image
        fields = ['id', 'title', 'image', 'uploaded_at']