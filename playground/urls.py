from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='quiz_index'),
    path('setup-players/', views.setup_players, name='quiz_setup_players'),
    path('submit-names/', views.submit_names, name='quiz_submit_names'),
    path('select-rounds/', views.select_rounds, name='quiz_select_rounds'),

    path('game/', views.game, name='quiz_game'),
    path('submit-answer/', views.submit_answer, name='quiz_submit_answer'),
    path('characters/', views.get_characters, name='quiz_characters'),
    path('results/', views.results, name='quiz_results'),
    path('new-game/', views.new_game, name='quiz_new_game'),
]
