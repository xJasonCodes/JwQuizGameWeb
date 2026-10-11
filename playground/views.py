from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from random import shuffle
import json

from .quiz_data import data

BIBLE_NAMES = [
    'Adam', 'Noah', 'Abraham', 'Isaac', 'Jacob', 'Esau', 'Levi', 'Judah', 'Reuben', 'Simeon',
    'Benjamin', 'Joseph', 'Gad', 'Asher', 'Issachar', 'Zebulun', 'Dan', 'Naphtali', 'Manasseh',
    'Ephraim', 'Aaron', 'Miriam', 'Joshua', 'Caleb', 'Samuel', 'Eli', 'David', 'Saul',
    'Jonathan', 'Solomon', 'Elijah', 'Elisha', 'Daniel', 'Esther', 'Mordecai', 'Nehemiah', 'Ezra',
    'Ruth', 'Naomi', 'Boaz', 'Mary', 'Joseph', 'Jesus', 'Peter', 'Paul', 'John', 'James',
    'Andrew', 'Philip', 'Bartholomew', 'Thomas', 'Matthew', 'Jude', 'Thaddaeus', 'Nathanael',
    'Lazarus', 'Mary Magdalene', 'Martha', 'Mark', 'Luke', 'Timothy', 'Titus', 'Silas',
    'Abel', 'Enoch', 'Methuselah', 'Shem', 'Ham', 'Japheth', 'Ishmael', 'Keturah', 'Midian',
    'Job', 'Bildad', 'Zophar', 'Elihu', 'Balak', 'Balaam', 'Jethro', 'Zipporah', 'Hobab',
    'Kenaz', 'Othniel', 'Ehud', 'Shamgar', 'Deborah', 'Gideon', 'Tola', 'Jair', 'Jephthah',
    'Ibzan', 'Elon', 'Abdon', 'Samson', 'Manoah', 'Delilah', 'Phinehas', 'Elkanah', 'Zadok',
    'Ahimaaz', 'Uriah', 'Bathsheba', 'Nathan', 'Joab', 'Abishai', 'Asahel', 'Amasa', 'Absalom',
    'Adonijah', 'Rehoboam', 'Jeroboam', 'Nadab', 'Baasha', 'Elah', 'Zimri', 'Omri', 'Ahab',
    'Jezebel', 'Athaliah', 'Ahaziah', 'Jehoram', 'Jehu', 'Jehoahaz', 'Jehoash', 'Jeroboam II',
    'Zachariah', 'Shallum', 'Menahem', 'Pekahiah', 'Pekah', 'Hoshea', 'Hezekiah', 'Manasseh',
    'Amon', 'Josiah', 'Jehoahaz', 'Jehoiachin', 'Zedekiah', 'Shemaiah', 'Huldah', 'Baruch',
    'Jeremiah', 'Lamentations', 'Ezekiel', 'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah',
    'Micah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai', 'Zechariah', 'Malachi', 'John Mark',
    'Barnabas', 'Junias', 'Andronicus', 'Herod', 'Herod Antipas', 'Herod Philip', 'Herod Agrippa',
    'Felix', 'Festus', 'Lysias', 'Tertullus', 'Ananias', 'Sapphira', 'Simon the Sorcerer',
    'Ethiopian Eunuch', 'Lydia', 'Phoebe', 'Euodia', 'Syntyche', 'Clement', 'Epaphras',
    'Archippus', 'Onesimus', 'Philemon', 'Apphia', 'Nymph', 'Nicanor', 'Parmenas', 'Prochorus',
    'Timon', 'Nicolaitan', 'Korah', 'Dathan', 'Abiram', 'Gehazi', 'Jezreel', 'Shaphat',
    'Eliab', 'Nethaneel', 'Jedeiah', 'Mattathias', 'Jozabad', 'Kolaiah', 'Neariah', 'Sabt',
    'Raamah', 'Sheba', 'Dedan', 'Asshur', 'Lud', 'Aram', 'Uz', 'Hul', 'Gether', 'Mash',
    'Anak', 'Shobal', 'Zibeon', 'Anah', 'Dishon', 'Amram', 'Jochebed', 'Elisheba', 'Nadab',
    'Abihu', 'Eleazar', 'Ithamar', 'Hur', 'Bezalel', 'Aholiab', 'Oholiab', 'Benaiah', 'Jehoiada',
    'Azariah', 'Jozadak', 'Josiah', 'Shallum', 'Amariah', 'Hilkiah', 'Meshullam', 'Zephaniah',
    'Shebaniah', 'Jehudi', 'Elnathan', 'Jehucal', 'Shaphan', 'Gemariah', 'Micaiah', 'Zephaniah',
    'Hanan', 'Tobijah', 'Jedaiah', 'Shiloni', 'Azrikam', 'Shemaiah', 'Urijah', 'Hozaham',
    'Shaphat', 'Adriel', 'Meholathite', 'Piram', 'Saphat', 'Sennacherib', 'Rabshakeh', 'Tartan',
    'Rabsaris', 'Nergalsharezer', 'Sherezer', 'Tamar', 'Shechem', 'Gideonite', 'Abiezrite',
    'Harorite', 'Shuhite', 'Anathothite', 'Mahathite', 'Korathite', 'Korahite', 'Sons of Korah',
    'Zerahite', 'Shilonite', 'Jeriel', 'Jahmai', 'Jibsam', 'Shemaiah', 'Jehiel', 'Zichri',
    'Abishua', 'Bukki', 'Uzzi', 'Zerahiah', 'Meraioth', 'Amariah', 'Ahitub', 'Zadok', 'Ahimaaz',
    'Azariah', 'Johanan', 'Azariah', 'Seriah', 'Jezreel', 'Ithamar', 'Dan', 'Gad', 'Naphtali',
    'Joseph', 'Benjamin', 'Zebulun', 'Asher', 'Judah', 'Levi', 'Issachar', 'Simeon', 'Reuben',
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
    all_hints_list = current_question_data[1:]
    
    current_player = player_names[current_player_index]
    current_hint = all_hints_list[min(hint_index, len(all_hints_list)-1)]
    
    request.session['current_answer'] = answer
    request.session['current_question_key'] = current_question_key
    request.session['all_hints'] = all_hints_list
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
        'all_hints': all_hints_list,
        'all_names': request.session.get('all_character_names', []),
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
            new_all_hints = []
            if new_question_counter < len(card_data):
                new_question_key = card_data[new_question_counter]
                new_question_data = data[new_question_key]
                new_all_hints = new_question_data[1:]
                new_hint = new_all_hints[min(new_hint_index, 9)]
            
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
                'new_hint': new_hint,
                'new_all_hints': new_all_hints
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
