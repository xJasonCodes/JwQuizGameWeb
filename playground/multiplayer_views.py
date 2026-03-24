from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.template import Library
import json
import uuid
import random

from .game_manager import GameManager
from .quiz_data import data

register = Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)

@register.filter
def times(number):
    return range(number)

@register.filter
def JSON_dump(obj):
    return json.dumps(obj)


def multiplayer_index(request):
    return render(request, 'quiz/multiplayer.html')


@require_http_methods(["GET", "POST"])
def host_game(request):
    if request.method == 'POST':
        timer_seconds = int(request.POST.get('timer_seconds', 15))
        
        room = GameManager.create_room("Host", timer_seconds)
        request.session['player_id'] = room.host_id
        request.session['room_code'] = room.room_code
        request.session['is_host'] = True
        
        return redirect('mp_host_lobby', room_code=room.room_code)
    
    return render(request, 'quiz/host_setup.html')


@require_http_methods(["GET", "POST"])
def join_game(request, room_code):
    room = GameManager.get_room(room_code)
    
    if not room:
        return render(request, 'quiz/error.html', {'message': 'Room not found'})
    
    if request.method == 'POST':
        player_name = request.POST.get('player_name', 'Player').strip()
        
        player_id = str(uuid.uuid4())
        room.add_pending_player(player_id, player_name)
        room.approve_player(player_id)
        
        request.session['player_id'] = player_id
        request.session['room_code'] = room_code
        request.session['is_host'] = False
        
        return redirect('mp_player', room_code=room_code)
    
    return render(request, 'quiz/join_game.html', {'room_code': room_code})


def join_game_get(request):
    room_code = request.GET.get('room_code', '')
    if room_code:
        return redirect('join_game', room_code=room_code)
    return redirect('multiplayer_index')


def host_lobby(request, room_code):
    room = GameManager.get_room(room_code)
    if not room:
        return redirect('multiplayer_index')
    
    if request.session.get('room_code') != room_code or not request.session.get('is_host'):
        return redirect('multiplayer_index')
    
    return render(request, 'quiz/host_lobby.html', {
        'room_code': room_code,
        'host_name': room.host_name,
        'players': room.players,
        'timer_seconds': room.timer_seconds
    })


def player_waiting(request, room_code):
    room = GameManager.get_room(room_code)
    if not room:
        return render(request, 'quiz/error.html', {'message': 'Room not found'})
    
    player_id = request.session.get('player_id')
    if not player_id or request.session.get('room_code') != room_code:
        return redirect('multiplayer_index')
    
    player_name = room.players.get(player_id, {}).get('name', 'Unknown')
    
    return render(request, 'quiz/player_waiting.html', {
        'room_code': room_code,
        'player_name': player_name,
        'host_name': room.host_name
    })


@require_http_methods(["POST"])
def start_multiplayer_game(request):
    room_code = request.POST.get('room_code')
    room = GameManager.get_room(room_code)
    
    if not room:
        return JsonResponse({'error': 'Room not found'}, status=404)
    
    if request.session.get('room_code') != room_code or not request.session.get('is_host'):
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    num_rounds = int(request.POST.get('num_rounds', 1))
    room.start_game(num_rounds)
    
    return JsonResponse({'success': True})


def game_state(request, room_code):
    room = GameManager.get_room(room_code)
    if not room:
        return JsonResponse({'error': 'Room not found'}, status=404)
    
    player_id = request.session.get('player_id')
    if not player_id or request.session.get('room_code') != room_code:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    state = room.get_state()
    state['is_host'] = request.session.get('is_host', False)
    state['my_id'] = player_id
    
    if room.status == 'playing':
        quiz_names = [data[key][0] for key in data]
        all_names = list(set(quiz_names + get_bible_names()))
        random.shuffle(all_names)
        state['all_names'] = sorted(all_names)
    
    return JsonResponse(state)


def get_bible_names():
    return [
        'Adam', 'Noah', 'Abraham', 'Isaac', 'Jacob', 'Esau', 'Levi', 'Judah', 'Reuben', 'Simeon',
        'Benjamin', 'Joseph', 'Gad', 'Asher', 'Issachar', 'Zebulun', 'Dan', 'Naphtali', 'Manasseh',
        'Ephraim', 'Aaron', 'Miriam', 'Joshua', 'Caleb', 'Samuel', 'Eli', 'David', 'Saul',
        'Jonathan', 'Solomon', 'Elijah', 'Elisha', 'Daniel', 'Esther', 'Mordecai', 'Nehemiah', 'Ezra',
        'Ruth', 'Naomi', 'Boaz', 'Mary', 'Joseph', 'Jesus', 'Peter', 'Paul', 'John', 'James'
    ]


@require_http_methods(["POST"])
def submit_multiplayer_answer(request):
    room_code = request.POST.get('room_code')
    room = GameManager.get_room(room_code)
    
    if not room:
        return JsonResponse({'error': 'Room not found'}, status=404)
    
    player_id = request.session.get('player_id')
    if not player_id:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    answer = request.POST.get('answer', '')
    result = room.submit_answer(player_id, answer)
    
    return JsonResponse(result)


@require_http_methods(["POST"])
def next_hint_multiplayer(request):
    room_code = request.POST.get('room_code')
    room = GameManager.get_room(room_code)
    
    if not room:
        return JsonResponse({'error': 'Room not found'}, status=404)
    
    if request.session.get('room_code') != room_code or not request.session.get('is_host'):
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    has_more = room.next_hint()
    
    if not has_more:
        room._move_to_next_question()
    
    return JsonResponse({'success': True, 'hint_index': room.hint_index})


@require_http_methods(["POST"])
def skip_player_multiplayer(request):
    room_code = request.POST.get('room_code')
    room = GameManager.get_room(room_code)
    
    if not room:
        return JsonResponse({'error': 'Room not found'}, status=404)
    
    if request.session.get('room_code') != room_code or not request.session.get('is_host'):
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    room.skip_to_next_player()
    
    return JsonResponse({'success': True})


def multiplayer_game(request, room_code):
    room = GameManager.get_room(room_code)
    if not room:
        return render(request, 'quiz/error.html', {'message': 'Room not found'})
    
    player_id = request.session.get('player_id')
    if not player_id or request.session.get('room_code') != room_code:
        return redirect('multiplayer_index')
    
    is_host = request.session.get('is_host', False)
    
    if room.status == 'waiting':
        if is_host:
            return redirect('mp_host_lobby', room_code=room_code)
        else:
            return redirect('mp_player', room_code=room_code)
    
    if room.status == 'finished':
        # Generate rankings
        player_list = [{'name': p['name'], 'score': p['score']} for p in room.players.values()]
        player_list.sort(key=lambda x: x['score'], reverse=True)
        rankings = [(p['name'], p['score']) for p in player_list]
        return render(request, 'quiz/results.html', {
            'rankings': rankings,
            'audio_file': '/static/audio/final_win.wav'
        })
    
    state = room.get_state()
    state['is_host'] = is_host
    state['my_id'] = player_id
    
    quiz_names = [data[key][0] for key in data]
    all_names = list(set(quiz_names + get_bible_names()))
    random.shuffle(all_names)
    state['all_names'] = sorted(all_names)
    
    return render(request, 'quiz/mp_game.html', state)
