from django.contrib import admin
from django.urls import path
from .views.AcceptRequest import AcceptRequest
from .views.CreateMatch import CreateMatch
from .views.EndMatch import EndMatch
from .views.ListFriends import ListFriends
from .views.MatchHistory import MatchHistory
from .views.SendRequest import SendRequest
from .views.UserStats import UserStats

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/stats/', UserStats, name='userstats'),

    # Match History
    path('user/matches/create/', CreateMatch, name='creatematch'),
    path('user/matches/end/',EndMatch,name='endmatch'),
    path('user/matches/', MatchHistory, name='matchhistory'),

    # Friendship
    path('user/friends/request/', SendRequest, name='sendrequest'),
    path('user/friends/accept/', AcceptRequest, name='acceptrequest'),
    path('user/friends/', ListFriends, name='listfriends'),
]
