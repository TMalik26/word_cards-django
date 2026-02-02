from django.urls import path

from game import views

app_name = 'game'

urlpatterns = [
    path('play/<int:session_id>/', views.play_game, name='play'),
    path('direction/<slug:topic_slug>/', views.choose_direction, name='direction'),
    path('result/<int:session_id>', views.game_result, name='result'),
]