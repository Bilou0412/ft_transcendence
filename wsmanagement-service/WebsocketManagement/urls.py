
from django.contrib import admin
from django.urls import path
from .views import FriendRequest

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ws/', FriendRequest, name="friendrequest"),
]
