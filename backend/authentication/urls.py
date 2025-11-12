# authentication/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterAPIView,
    LoginAPIView,
    VerifyEmailAPIView,
    ResendVerificationEmailAPIView,
    GoogleAuthAPIView,
    VerifyTokenAPIView,
    LogoutAPIView,
    UpdateProfileAPIView,
    GetFormChoicesAPIView,
    HealthCheckAPIView,
)

app_name = 'authentication'

urlpatterns = [
    # Health check
    path('health/', HealthCheckAPIView.as_view(), name='health-check'),
    
    # Email/Password Authentication
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    
    # Profile Management
    path('profile/', UpdateProfileAPIView.as_view(), name='update-profile'),
    path('form-choices/', GetFormChoicesAPIView.as_view(), name='form-choices'),
    
    # Email Verification
    path('verify-email/', VerifyEmailAPIView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationEmailAPIView.as_view(), name='resend-verification'),
    
    # Token Verification
    path('verify/', VerifyTokenAPIView.as_view(), name='verify-token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # Social Authentication
    path('google/', GoogleAuthAPIView.as_view(), name='google-auth'),
]