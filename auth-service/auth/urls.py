from django.contrib import admin
from django.urls import path
from .views.auth import token ,signup,logout
from .views.token_management import refresh_token, validate_token
from .views.email_verification import email_verification,reset_password_confirm
from .views.password_management import reset_password_request, change_password
from .views.auth42 import UserCreateFrom42View
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
   # Admin URL
   path('admin/', admin.site.urls),
   # API Authentication endpoints
   path('api/auth/login/', token, name='login'),
   path('api/auth/signup/', signup, name='signup'),
   path('api/auth/email_verification/<str:uidb64>/<str:token>/', email_verification, name='email_verification'),
   
   # API Token endpoint
   path('api/auth/token/refresh/', refresh_token, name='token_refresh'),
   path('api/auth/token/validate/', validate_token, name='token_validate'),
   
   # API Password reset endpoints
   path('api/auth/password/reset/', reset_password_request, name='password_reset_request'),
   path('api/auth/password/reset/confirm/<str:uidb64>/<str:token>/', reset_password_confirm, name='password_reset_confirm'),
   path('api/auth/password/change/', change_password, name='change_password'),
   
   # API 42OAuth
   path('api/auth/form42/', UserCreateFrom42View, name='oauth42_callback'),
   
   # API Logout endpoint
   path('api/auth/logout/', logout, name='logout'),
   path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
   path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

 

]
