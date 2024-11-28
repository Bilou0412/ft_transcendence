from django.contrib import admin
from django.urls import path
from .views.UpdateFriendshipStatus import UpdateFriendshipStatus
from .views.CreateMatch import CreateMatch
from .views.MatchHistory import MatchHistory
from .views.ListFriends import ListFriends
##from .views.MatchHistory import MatchHistory
from .views.SendRequest import SendRequest
from .views.UserStats import UserStats

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/stats/', UserStats, name='userstats'),

    # Match History
    path('user/matches/create/', CreateMatch, name='creatematch'),
    path('user/<int:user_id>/matches/', MatchHistory, name='get_user_match_history'),
   # path('user/matches/', MatchHistory, name='matchhistory'),

    # Friendship
    path('user/friends/request/', SendRequest, name='sendrequest'),
    path('user/friends/update/', UpdateFriendshipStatus, name='acceptrequest'),
    path('user/friends/', ListFriends, name='listfriends'),
]
