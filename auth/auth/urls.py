from django.contrib import admin
from django.urls import path
from . import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="auth API",
      default_version='v1',
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
   
]

urlpatterns = [
    # Admin URL
    path('admin/', admin.site.urls),

    # API Authentication endpoints
    path('api/auth/login/', views.token, name='login'),
    path('api/auth/signup/', views.signup, name='signup'),
    path('api/auth/email_verification/<str:uidb64>/<str:token>/', views.email_verification, name='email_verification'),
    
    # API Token endpoint
    path('api/auth/token/refresh/', views.refresh_token, name='token_refresh'),
    path('api/auth/token/validate/', views.validate_token, name='token_validate'),
    
    # API Password reset endpoints
    path('api/auth/password/reset/', views.reset_password_request, name='password_reset_request'),
    path('api/auth/password/reset/confirm/<str:uidb64>/<str:token>/', views.reset_password_confirm, name='password_reset_confirm'),
    path('api/auth/password/change/', views.change_password, name='change_password'),

    # API Logout endpoint
    path('api/auth/logout/', views.logout, name='logout'),

    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
