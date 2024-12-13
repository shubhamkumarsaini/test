from django.urls import path
from . import views

urlpatterns = [
    path('', views.daily_game, name='daily_game'),
    path('past_game/<int:game_id>/', views.past_game, name='past_game'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('submit_guess/<int:game_id>/', views.submit_guess, name='submit_guess'),
    path('submit_guesspast/<int:game_id>/', views.submit_guesspast, name='submit_guesspast'),
    path('statistics/', views.user_statistics, name='user_statistics'),
    path('calendar/', views.calendar_view, name='calendar'),
]


