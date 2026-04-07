# accounts/urls.py

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    AdminUsersListView,
    ChangePasswordView,
    SignupGroupsView,
    SignupView,
    UserDetailView,
)

urlpatterns = [
    # JWT endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User registration
    path('signup-groups/', SignupGroupsView.as_view(), name='signup_groups'),
    path('signup/', SignupView.as_view(), name='user_signup'),
    path('me/', UserDetailView.as_view(), name='user_detail'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('admin/users/', AdminUsersListView.as_view(), name='admin_users'),
]
