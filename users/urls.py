from django.urls import path
from django.urls import path, include
from .api.views import (
        RegisterAPIView,
        LoginAPIView,
        CustomUserAPIView,
)

account_api_urls = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('', CustomUserAPIView.as_view(), name='users'),
]


urlpatterns = [
    path('', include(account_api_urls)),
]

