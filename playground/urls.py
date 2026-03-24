from django.urls import path
from . import views, multiplayer_views as mp_views

urlpatterns = [
    # Single player
    path('', views.index, name='quiz_index'),
    path('setup-players/', views.setup_players, name='quiz_setup_players'),
    path('submit-names/', views.submit_names, name='quiz_submit_names'),
    path('select-rounds/', views.select_rounds, name='quiz_select_rounds'),
    path('game/', views.game, name='quiz_game'),
    path('submit-answer/', views.submit_answer, name='quiz_submit_answer'),
    path('characters/', views.get_characters, name='quiz_characters'),
    path('results/', views.results, name='quiz_results'),
    path('new-game/', views.new_game, name='quiz_new_game'),
    
    # Multiplayer
    path('multiplayer/', mp_views.multiplayer_index, name='multiplayer_index'),
    path('multiplayer/host/', mp_views.host_game, name='host_game'),
    path('multiplayer/join/', mp_views.join_game_get, name='join_game_get'),
    path('multiplayer/join/<str:room_code>/', mp_views.join_game, name='join_game'),
    path('multiplayer/host/lobby/<str:room_code>/', mp_views.host_lobby, name='mp_host_lobby'),
    path('multiplayer/player/waiting/<str:room_code>/', mp_views.player_waiting, name='mp_player'),
    path('multiplayer/start/', mp_views.start_multiplayer_game, name='mp_start_game'),
    path('multiplayer/state/<str:room_code>/', mp_views.game_state, name='mp_game_state'),
    path('multiplayer/submit/', mp_views.submit_multiplayer_answer, name='mp_submit_answer'),
    path('multiplayer/next-hint/', mp_views.next_hint_multiplayer, name='mp_next_hint'),
    path('multiplayer/skip/', mp_views.skip_player_multiplayer, name='mp_skip_player'),
    path('multiplayer/game/<str:room_code>/', mp_views.multiplayer_game, name='mp_game'),
]
