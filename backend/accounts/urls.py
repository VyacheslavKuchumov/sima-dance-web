# accounts/urls.py

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import UserDetailView, SignupView  # optional, see step 3

urlpatterns = [
    # JWT endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User registration
    path('signup/', SignupView.as_view(), name='user_signup'),
    path('me/', UserDetailView.as_view(), name='user_detail'),
]
