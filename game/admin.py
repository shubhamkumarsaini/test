from django.contrib import admin
from .models import *

admin.site.register([User,Genre,TVShow,Episode,EpisodeImage,DailyGame,UserGameHistory,UserStatistics])