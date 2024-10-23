
from django.contrib import admin
from django.urls import re_path
from . import views

urlpatterns = [
    re_path('auth/token', views.token),
    re_path('auth/signup', views.signup),
    re_path('auth/refresh', views.refresh_token),
]
