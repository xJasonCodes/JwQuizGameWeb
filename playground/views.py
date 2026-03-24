from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from random import shuffle
import json

from .quiz_data import data

BIBLE_NAMES = [
    'Adam', 'Noah', 'Abraham', 'Isaac', 'Jacob', 'Esau', 'Levi', 'Judah', 'Reuben', 'Simeon',
    'Benjamin', 'Joseph', 'Benjamin', 'Gad', 'Asher', 'Issachar', 'Zebulun', 'Dan', 'Naphtali', 'Manasseh',
    'Ephraim', 'Aaron', 'Miriam', 'Korah', 'Bezalel', 'Aholiab', 'Joshua', 'Caleb', 'Nun', 'Eleazar',
    'Phinehas', 'Deborah', 'Barak', 'Sisera', 'Jael', 'Gideon', 'Abimelech', 'Tola', 'Jair', 'Jepthah',
    'Ibzan', 'Elon', 'Abdon', 'Samson', 'Delilah', 'Hannah', 'Elkanah', 'Peninnah', 'Samuel', 'Eli',
    'Hophni', 'Phinehas', 'David', 'Saul', 'Jonathan', 'Abner', 'Joab', 'Abishai', 'Asahel', 'Benaiah',
    'Nathan', 'Gad', 'Iddo', 'Ahijah', 'Shemaiah', 'Iddan', 'Heman', 'Jeduthun', 'Asaph', 'Solomon',
    'Rehoboam', 'Jeroboam', 'Nadab', 'Baasha', 'Elah', 'Zimri', 'Omri', 'Ahab', 'Jezebel', 'Elijah',
    'Elisha', 'Micaiah', 'Amaziah', 'Azariah', 'Jotham', 'Ahaz', 'Hezekiah', 'Manasseh', 'Amon', 'Josiah',
    'Jehoahaz', 'Jehoiakim', 'Jehoiachin', 'Zedekiah', 'Jeremiah', 'Baruch', ' Seraiah', 'Ezekiel', 'Daniel',
    'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai',
    'Zechariah', 'Malachi', 'Esther', 'Mordecai', 'Haman', 'Vashti', 'Nehemiah', 'Ezra', 'Meshach', 'Abednego',
    'Shadrach', 'Azariah', 'Hananiah', 'Mishael', 'Isaiah', 'Jeremiah', 'Ezekiel', 'Daniel', 'Hosea', 'Joel',
    'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai', 'Zechariah', 'Malachi',
    'Ruth', 'Naomi', 'Boaz', 'Orpah', 'Mahlon', 'Chilion', 'Tamar', 'Onan', 'Er', 'Shelah',
    'Obed', 'Jesse', 'Abigail', 'Nabal', 'Uriah', 'Bathsheba', 'Amnon', 'Absalom', 'Adonijah', 'Amariah',
    'Zadok', 'Ahimelech', 'Doeg', 'Abiathar', 'Ittai', 'Hushai', 'Ahithophel', 'Ziba', 'Mephibosheth', 'Mephibosheth',
    'Cornelius', 'Ananias', 'Sapphira', 'Stephen', 'Philip', 'Prochorus', 'Nicanor', 'Timon', 'Parmenas', 'Nicolas',
    'Barnabas', 'Joseph', 'Mark', 'John', 'Paul', 'Timothy', 'Titus', 'Silas', 'Luke', 'Jason',
    'Sopater', 'Crispus', 'Gaius', 'Secundus', 'Epaphroditus', 'Archippus', 'Philemon', ' Onesimus', 'Archelaus', 'Herod',
    'Herod Antipas', 'Herod Agrippa', 'Salome', 'Jairus', 'Zacchaeus', 'Bartimaeus', 'Lazarus', 'Mary', 'Martha',
    'Nicodemus', 'Gamaliel', 'Ananias', 'Felix', 'Festus', 'Agrippa', 'Tertullus', 'Apollos', 'Cephas', 'Nathanael',
    'Thomas', 'Matthew', 'James', 'Jude', 'Thaddaeus', 'Simon', 'Andrew', 'Philip', 'Bartholomew', 'Lebbaeus',
    'Anna', 'Simeon', 'Elizabeth', 'Zacharias', 'Gabriel', 'Herod the Great', 'Cleopas', 'Nathanael', 'Candace', 'Ethiopian'
]


def get_all_character_names():
    quiz_names = [data[key][0] for key in data]
    all_names = list(set(quiz_names + BIBLE_NAMES))
    shuffle(all_names)
    return sorted(all_names), quiz_names


def index(request):
    request.session.flush()
    return render(request, 'quiz/setup.html')


def setup_players(request):
    if request.method == 'POST':
        num_players = int(request.POST.get('num_players', 1))
        all_names, _ = get_all_character_names()
        request.session['num_players'] = num_players
        request.session['all_character_names'] = all_names
        request.session['player_names'] = []
        request.session['player_scores'] = {}
        request.session['max_rounds'] = len(data) // num_players
        return render(request, 'quiz/player_names.html', {
            'num_players': num_players,
            'max_rounds': request.session['max_rounds']
        })
    return redirect('quiz_index')


def submit_names(request):
    if request.method == 'POST':
        player_names = []
        for i in range(request.session['num_players']):
            name = request.POST.get(f'player_{i}', f'Player {i+1}').strip()
            if not name:
                name = f'Player {i+1}'
            player_names.append(name)
        
        request.session['player_names'] = player_names
        request.session['player_scores'] = {name: 0 for name in player_names}
        
        card_keys = list(data.keys())
        shuffle(card_keys)
        request.session['card_data'] = card_keys
        request.session['question_counter'] = 0
        request.session['current_round'] = 1
        request.session['current_player_index'] = 0
        request.session['hint_index'] = 0
        request.session['num_rounds'] = 1
        
        return redirect('quiz_select_rounds')
    return redirect('quiz_index')


def select_rounds(request):
    if 'player_names' not in request.session:
        return redirect('quiz_index')
    
    max_rounds = request.session.get('max_rounds', 1)
    player_names = request.session['player_names']
    
    if request.method == 'POST':
        num_rounds = int(request.POST.get('num_rounds', 1))
        request.session['num_rounds'] = num_rounds
        return redirect('quiz_game')
    
    return render(request, 'quiz/select_rounds.html', {
        'max_rounds': max_rounds,
        'player_names': player_names
    })


def game(request):
    if 'card_data' not in request.session:
        return redirect('quiz_index')
    
    num_rounds = request.session.get('num_rounds', 1)
    num_players = len(request.session['player_names'])
    question_counter = int(request.session.get('question_counter', 0))
    current_player_index = int(request.session.get('current_player_index', 0))
    current_round = int(request.session.get('current_round', 1))
    player_names = request.session['player_names']
    player_scores = request.session['player_scores']
    card_data = request.session['card_data']
    hint_index = int(request.session.get('hint_index', 0))
    
    if question_counter >= len(card_data) or (question_counter // num_players) >= num_rounds:
        return redirect('quiz_results')
    
    current_question_key = card_data[question_counter]
    current_question_data = data[current_question_key]
    answer = current_question_data[0]
    all_hints = current_question_data[1:]
    
    current_player = player_names[current_player_index]
    current_hint = all_hints[min(hint_index, len(all_hints)-1)]
    
    request.session['current_answer'] = answer
    request.session['current_question_key'] = current_question_key
    request.session.save()
    
    return render(request, 'quiz/game.html', {
        'current_player': current_player,
        'player_scores': player_scores,
        'player_names': player_names,
        'current_round': current_round,
        'num_rounds': num_rounds,
        'question_number': question_counter + 1,
        'total_questions': num_rounds * num_players,
        'current_hint': current_hint,
        'hint_number': hint_index + 1,
        'max_score': 10 - hint_index,
        'all_names': json.dumps(request.session.get('all_character_names', [])),
        'audio_files': {
            'correct': '/static/audio/correct.wav',
            'wrong': '/static/audio/wrong.wav',
            'background': '/static/audio/background_1.wav'
        }
    })


@csrf_exempt
@require_http_methods(["POST"])
def submit_answer(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            guess = json_data.get('guess', '')
            skip = guess == '__SKIP__'
            
            current_answer = request.session.get('current_answer', '')
            hint_index = request.session.get('hint_index', 0)
            current_player_index = request.session['current_player_index']
            question_counter = request.session['question_counter']
            player_names = request.session['player_names']
            player_scores = request.session['player_scores']
            num_rounds = request.session.get('num_rounds', 1)
            card_data = request.session['card_data']
            num_players = len(player_names)
            
            correct = guess.lower().strip() == current_answer.lower().strip() if not skip else False
            points = 0
            action = None
            
            if correct:
                action = 'correct'
                points = 10 - hint_index
                player_scores[player_names[current_player_index]] += points
                request.session['player_scores'] = player_scores
                request.session['question_counter'] = question_counter + 1
                request.session['current_player_index'] = (current_player_index + 1) % num_players
                request.session['hint_index'] = 0
                request.session.modified = True
            elif skip:
                action = 'next_hint'
                if hint_index >= 9:
                    request.session['question_counter'] = question_counter + 1
                    request.session['current_player_index'] = (current_player_index + 1) % num_players
                    request.session['hint_index'] = 0
                    action = 'next_question'
                else:
                    request.session['hint_index'] = hint_index + 1
                request.session.modified = True
            else:
                action = 'wrong_guess'
                if hint_index >= 9:
                    request.session['question_counter'] = question_counter + 1
                    request.session['current_player_index'] = (current_player_index + 1) % num_players
                    request.session['hint_index'] = 0
                    action = 'failed_all_hints'
                else:
                    request.session['hint_index'] = hint_index + 1
                request.session.modified = True
            
            if request.session['question_counter'] < len(card_data):
                request.session['current_round'] = (request.session['question_counter'] // num_players) + 1
            
            request.session.save()
            
            game_over = (request.session['question_counter'] >= len(card_data) or 
                        (request.session['question_counter'] // num_players) >= num_rounds)
            
            new_hint_index = request.session.get('hint_index', 0)
            new_question_counter = request.session.get('question_counter', 0)
            new_player_index = request.session.get('current_player_index', 0)
            new_round = request.session.get('current_round', 1)
            
            new_hint = ''
            if new_question_counter < len(card_data):
                new_question_key = card_data[new_question_counter]
                new_question_data = data[new_question_key]
                new_hint = new_question_data[1:][min(new_hint_index, 9)]
            
            return JsonResponse({
                'correct': correct,
                'points': points,
                'action': action,
                'answer': current_answer if action in ['failed_all_hints'] else None,
                'game_over': game_over,
                'new_hint_index': new_hint_index,
                'new_question_counter': new_question_counter,
                'new_player_index': new_player_index,
                'new_round': new_round,
                'new_player_name': player_names[new_player_index],
                'new_max_score': 10 - new_hint_index,
                'new_hint': new_hint
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid method'}, status=405)


@csrf_exempt
@require_http_methods(["GET"])
def get_characters(request):
    return JsonResponse({
        'names': request.session.get('all_character_names', [])
    })


def results(request):
    if 'player_scores' not in request.session:
        return redirect('quiz_index')
    
    player_scores = request.session['player_scores']
    ranked = sorted(player_scores.items(), key=lambda item: item[1], reverse=True)
    
    return render(request, 'quiz/results.html', {
        'rankings': ranked,
        'audio_file': '/static/audio/final_win.wav'
    })


def new_game(request):
    request.session.flush()
    return redirect('quiz_index')
