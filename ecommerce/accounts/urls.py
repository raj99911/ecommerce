from django.urls import path,include
from .views import LoginAPIView, UserRegistration, ProfileView, Dashboard,LogoutView

from rest_framework_simplejwt.views import  (
    TokenObtainPairView,TokenRefreshView
)


urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('register/', UserRegistration.as_view(), name='register'),
    path('token/',TokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('token/refresh/',TokenRefreshView.as_view(),name='token_refresh_view'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('dashboard/',Dashboard.as_view(),name='dashboard'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
]

