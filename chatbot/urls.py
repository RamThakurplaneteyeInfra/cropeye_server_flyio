from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import chatbot_api, ChatbotConfigViewSet

router = DefaultRouter()
router.register(r'chatbot-configurations', ChatbotConfigViewSet, basename='chatbotconfig')

urlpatterns = [
    path('chatbot/', chatbot_api, name='chatbot-api'),
    path('', include(router.urls)),
]

