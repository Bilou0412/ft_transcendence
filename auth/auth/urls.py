
from django.contrib import admin
from django.urls import re_path ,path
from . import views

urlpatterns = [
    re_path('auth/token', views.token),
    re_path('auth/signup', views.signup),
    re_path('auth/refresh', views.refresh_token),
    re_path('auth/reset-password', views.reset_password_request_view, name='reset_password'),
    
    # Expression régulière ajustée pour capturer des tokens de longueur variable
    re_path(r'^auth/password-confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', views.reset_password_confirm, name='password_reset_confirm'),
    
    path('admin/', admin.site.urls),
]
