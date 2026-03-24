import random
import uuid
from datetime import datetime
from .quiz_data import data as quiz_data

class GameRoom:
    def __init__(self, room_code, host_name, timer_seconds=15):
        self.room_code = room_code
        self.host_name = host_name
        self.host_id = str(uuid.uuid4())
        self.players = {}  # Host is NOT a player - just controls the game
        self.pending_players = {}
        self.status = 'waiting'  # waiting, playing, finished
        self.timer_seconds = timer_seconds
        self.current_round = 0
        self.num_rounds = 1
        self.question_index = 0
        self.hint_index = 0
        self.current_player_id = None
        self.card_data = list(quiz_data.keys())
        random.shuffle(self.card_data)
        self.current_question = None
        self.current_hints = []
        self.created_at = datetime.now()
        self.last_sound = None  # Track what sound should play
        self.sound_played_ids = set()  # Track which sounds have been played
    
    def add_pending_player(self, player_id, player_name):
        self.pending_players[player_id] = {'name': player_name}
    
    def approve_player(self, player_id):
        if player_id in self.pending_players:
            player_data = self.pending_players[player_id].copy()
            player_data['score'] = 0
            self.players[player_id] = player_data
            del self.pending_players[player_id]
            return True
        return False
    
    def remove_player(self, player_id):
        if player_id in self.players:
            del self.players[player_id]
            return True
        return False
    
    def start_game(self, num_rounds):
        if len(self.players) == 0:
            return False
        self.num_rounds = min(num_rounds, len(self.card_data))
        self.status = 'playing'
        self.current_round = 1
        self.question_index = 0
        self.hint_index = 0
        self._load_current_question()
        return True
    
    def _load_current_question(self):
        if self.question_index >= len(self.card_data) or self.current_round > self.num_rounds:
            self.status = 'finished'
            self.current_question = None
            return
        
        key = self.card_data[self.question_index]
        self.current_question = quiz_data[key]
        self.current_hints = self.current_question[1:11]
        
        if not self.current_player_id and self.players:
            self.current_player_id = list(self.players.keys())[0]
    
    def next_hint(self):
        if self.hint_index < 9:
            self.hint_index += 1
            return True
        return False
    
    def skip_to_next_player(self):
        player_ids = list(self.players.keys())
        current_idx = player_ids.index(self.current_player_id) if self.current_player_id in player_ids else -1
        next_idx = (current_idx + 1) % len(player_ids)
        self.current_player_id = player_ids[next_idx]
        self.hint_index = 0
    
    def submit_answer(self, player_id, answer):
        if player_id != self.current_player_id:
            return {'success': False, 'message': 'Not your turn'}
        
        if not self.current_question:
            return {'success': False, 'message': 'No active question'}
        
        correct_answer = self.current_question[0].lower()
        if answer.lower().strip() == correct_answer:
            points = 10 - self.hint_index
            self.players[player_id]['score'] += points
            self.last_sound = 'correct'
            self._move_to_next_question()
            return {'success': True, 'correct': True, 'points': points}
        
        if self.hint_index >= 9:
            self.last_sound = 'wrong'
            self._move_to_next_question()
            return {'success': True, 'correct': False, 'message': 'Out of hints'}
        
        # Actually advance to next hint when wrong answer
        self.hint_index += 1
        self.last_sound = 'wrong'
        return {'success': True, 'correct': False, 'hint_index': self.hint_index}
    
    def _move_to_next_question(self):
        self.question_index += 1
        self.hint_index = 0
        
        if self.question_index >= len(self.card_data) or (self.question_index // max(1, len(self.players))) + 1 > self.num_rounds:
            self.status = 'finished'
            self.current_question = None
            self.last_sound = 'finished'
            return
        
        if self.players:
            self.current_round = (self.question_index // len(self.players)) + 1
            player_ids = list(self.players.keys())
            current_idx = player_ids.index(self.current_player_id) if self.current_player_id in player_ids else 0
            next_idx = (current_idx + 1) % len(player_ids)
            self.current_player_id = player_ids[next_idx]
        self._load_current_question()
    
    def get_state(self):
        player_list = [{'id': pid, 'name': p['name'], 'score': p['score']} for pid, p in self.players.items()]
        
        sound_to_play = self.last_sound
        sound_id = f"{self.question_index}_{self.hint_index}_{self.last_sound}"
        
        state = {
            'room_code': self.room_code,
            'status': self.status,
            'players': player_list,
            'current_round': self.current_round,
            'num_rounds': self.num_rounds,
            'current_player_id': self.current_player_id,
            'timer_seconds': self.timer_seconds,
            'sound': sound_to_play,
            'sound_id': sound_id,
        }
        
        if self.status == 'playing' and self.current_question:
            state['question'] = {
                'hint': self.current_hints[self.hint_index] if self.hint_index < len(self.current_hints) else '',
                'hint_number': self.hint_index + 1,
                'max_score': 10 - self.hint_index,
                'answer': self.current_question[0] if self.status == 'finished' else None
            }
        
        return state


class GameManager:
    _rooms = {}
    
    @classmethod
    def generate_room_code(cls):
        while True:
            code = str(random.randint(1000, 9999))
            if code not in cls._rooms:
                return code
    
    @classmethod
    def create_room(cls, host_name, timer_seconds=15):
        room_code = cls.generate_room_code()
        room = GameRoom(room_code, host_name, timer_seconds)
        cls._rooms[room_code] = room
        return room
    
    @classmethod
    def get_room(cls, room_code):
        return cls._rooms.get(room_code)
    
    @classmethod
    def delete_room(cls, room_code):
        if room_code in cls._rooms:
            del cls._rooms[room_code]
    
    @classmethod
    def room_exists(cls, room_code):
        return room_code in cls._rooms
