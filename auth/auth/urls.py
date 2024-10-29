from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # Admin URL
    path('admin/', admin.site.urls),

    # API Authentication endpoints
    path('api/auth/login/', views.token, name='login'),
    path('api/auth/signup/', views.signup, name='signup'),
    path('api/auth/email_verification/<str:uidb64>/<str:token>/', views.email_verification, name='email_verification'),
    path('api/auth/token/refresh/', views.refresh_token, name='token_refresh'),

    # API Password reset endpoints
    path('api/auth/password/reset/', views.reset_password_request, name='password_reset_request'),
    path('api/auth/password/reset/confirm/<str:uidb64>/<str:token>/', views.reset_password_confirm, name='password_reset_confirm'),
    path('api/auth/password/change/', views.change_password, name='change_password'),

    # API Logout endpoint
    # path('api/auth/logout/', views.logout, name='logout'),

]
