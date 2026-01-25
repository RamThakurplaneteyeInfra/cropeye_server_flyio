from rest_framework import serializers
from .models import ChatbotConfig


class ChatbotConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotConfig
        fields = [
            'id', 'model_name', 'api_url', 'is_active',
            'timeout_seconds', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
