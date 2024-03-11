from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from .views import CustomTokenObtainPairView, signup, FetchAlertsView, CreateAlertView, RegistrationAPIView, RestrictedView, FilterFetchAlertsView, DeleteAlertView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("", views.index, name="index"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', RegistrationAPIView.as_view(), name="register"),
    path('auth/login/', TokenObtainPairView.as_view(), name="auth_login"),
    path('auth/refresh-token', TokenRefreshView.as_view(), name="auth_refresh"),
    path('api/restricted', RestrictedView.as_view(), name ='restricted'),
    #path('login/', LoginView.as_view(), name='login'),
    #path('logout/', LogoutView.as_view(), name='logout'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('signup/', signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    #path('alerts/create/', views.create_alert, name='create_alert'),
    path('alerts/create/', CreateAlertView.as_view(), name='create_alert'),
    path('alerts/delete/', views.DeleteAlertView.as_view(), name='delete_alert'),
    path('fetchalerts/', FetchAlertsView.as_view(), name='fetch_alerts'),
    path('alerts/filter-fetch/', FilterFetchAlertsView.as_view(), name='filter fetch alerts'),
    path('fetch_price', views.fetch_coingecko_prices, name='fetch_current_prices')
]