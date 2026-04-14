from django.urls import path
from .views import CustomTokenObtainPairView, UserRegistrationview, UserProfileView, UserProfileUpdateView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('register/', UserRegistrationview.as_view(), name='user-register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('profile/', UserProfileUpdateView.as_view(), name='user-profile-update'),
]
