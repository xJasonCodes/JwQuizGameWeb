# JwQuizGameWeb

A Bible character guessing game I built for family worship. You get up to 10 hints per round, fewer hints used means more points. Works solo with friends on one screen, or multiplayer over the local network with one person hosting.

## How it plays

Single player: pick how many players and rounds, enter names, then take turns guessing the character from the hints. 10 points if you get it on the first hint, down to 1 point on the last one.

Multiplayer: one person hits Create Game and gets a 4-digit room code plus a timer setting. Everyone else joins with the code. The host doesn't play, they just run the game with Next Hint / Skip buttons. Players answer on their own devices when it's their turn.

## Running it

Needs Python 3.12 and pip.

```
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Then open http://127.0.0.1:8000/playground/

For playing with others on the same wifi, run it open to the network and share your IP:

```
python manage.py runserver 0.0.0.0:8080
```

Then everyone goes to `http://YOUR-IP:8080/playground/multiplayer/` and joins with the room code.

## Settings

I keep secrets out of the code, so these come from the environment with sensible defaults for local play:

```
DJANGO_SECRET_KEY=something-long-and-random
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=*
```

On Windows PowerShell that looks like:

```
$env:DJANGO_SECRET_KEY="your-key-here"
python manage.py runserver
```

## Audio

The background music files are pretty big, so they're stored with Git LFS. After cloning, make sure you have Git LFS installed and run:

```
git lfs pull
```

If the sounds don't play, check `static/audio/` actually has the .wav files and not just pointer text.

## Layout

- `playground/views.py` - single player game flow
- `playground/multiplayer_views.py` + `game_manager.py` - rooms, turns, scoring for multiplayer
- `playground/quiz_data.py` - the characters and hints
- `playground/templates/quiz/` - all the pages
- `storefront/settings.py` - Django settings

## License

MIT, see LICENSE.
