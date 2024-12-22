from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO
import time
from threading import Thread, Event
from queue import Queue
import torch
import os

from game import Game
from agent import Agent
from helper import extract_number, plot_train

dir_model='./model'
os.makedirs(os.path.dirname(dir_model), exist_ok=True)

app = Flask(__name__)
socketio = SocketIO(app)

app.config['game_thread'] = None
app.config['stop_event'] = Event()  # Signals when to stop the thread
app.config['pause_event'] = Event()  # Signals when to pause/resume the thread
app.config['pause_event'].set()  # Initially set, meaning "not paused"
app.config['queue'] = Queue()
app.config['turn']=None

@app.route("/", methods=["GET", "POST"])
def index():
    models = [f for f in os.listdir(dir_model) if f.endswith('.pt')]
    models=sorted(models, key=extract_number)
    return render_template("index.html", models=models)

@app.route("/start_thread", methods=["POST"])
def start_thread():
    app.config['queue']=Queue() # reset app.config['queue'] to avoid the command from last game
    # global thread, thread_running
    '''once a thread is started, you cannot restart it. If you call /start_thread multiple times, it tries to start the same thread object again, which is not allowed. To fix this, you need to manage the thread properly, ensuring:
    You don’t start multiple threads for the same task.
    You can reuse the endpoint without creating new threads.'''
    speed=int(request.json.get('speed'))
    mode=request.json.get('mode')
    model_name=request.json.get('model')
    if app.config['game_thread'] is None or not app.config['game_thread'].is_alive():
        # Reset stop and pause events
        app.config['stop_event'].clear()
        app.config['pause_event'].set()

        # Start the game thread
        if mode=='human':
            game_thread = Thread(target=play, args=(speed,))
        elif mode=='robot':
            game_thread = Thread(target=train, args=(speed, model_name))
        game_thread.daemon = True
        game_thread.start()
        app.config['game_thread'] = game_thread
        return '', 204
    else:
        return '', 304

@app.route("/stop_thread", methods=["GET"])
def stop_thread():
    app.config['stop_event'].set()
    return '', 204

@app.route("/pause_resume_thread", methods=["GET"])
def thread_action():
    action = request.args.get('action')
    if action == "pause":
        app.config['pause_event'].clear()
    elif action == "resume":
        app.config['pause_event'].set()
    return '', 204

@app.route("/turn", methods=["POST"])
def turn():
    app.config['queue'].put(request.json.get('direction'))
    return '', 204

def play(speed):
    game=Game()
    while not app.config['stop_event'].is_set():  # Check if thread should stop
        # Wait here if the thread is paused
        app.config['pause_event'].wait()
        turn=None
        try:
            # Non-blocking check for a new direction
            turn = app.config['queue'].get_nowait()
        except Exception:
            pass
        reward, game_over, score, body, food = game.play_step(turn)
        if game_over == True:
            # tell frontend it is over by sending scorePy=-1
            socketio.emit('snake_info', {'scorePy':-1})
            break
        socketio.emit('snake_info', {'body':body, 'food':food, 'scorePy':score})
        time.sleep(0.5/speed)

def train(speed, model_name):
    scores = []
    mean_scores = []
    total_score = 0
    record = 0
    if model_name in os.listdir(dir_model):
        model=torch.load(os.path.join(dir_model, model_name))
    else:
        model=None
    agent = Agent(model)
    game = Game()
    
    while not app.config['stop_event'].is_set():  # Check if thread should stop
        # Wait here if the thread is paused
        app.config['pause_event'].wait()
        state_old = agent.get_state(game)
        final_move = agent.get_action(state_old)
        # perform move and get new state
        turn=None
        if final_move[0]==1:
            turn='left'
        if final_move[-1]==1:
            turn='right'
        reward, game_over, score, body, food = game.play_step(turn)
        state_new = agent.get_state(game)
        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, game_over)
        # remember
        agent.remember(state_old, final_move, reward, state_new, game_over)
        socketio.emit('snake_info', {'body':body, 'food':food, 'scorePy':score})
        time.sleep(0.5/speed)
        if game_over:
            # train long memory, plot result
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()
            if score > record:
                record = score
                models = [f for f in os.listdir(dir_model) if f.endswith('.pt')]
                models=sorted(models, key=extract_number)
                if extract_number(models[-1])<score:
                    torch.save(agent.model, f'{dir_model}/model_{score}.pt')
            # print('Game', agent.n_games, 'Score', score, 'Record:', record)
            scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            mean_scores.append(mean_score)
            socketio.emit('snake_info',{'scorePy':-1,'plot':plot_train(scores, mean_scores)})

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5001, host="0.0.0.0", allow_unsafe_werkzeug=True)
    # app.run(debug=True, port=5001, host="0.0.0.0")

# in one move press left twice, it will turn twice in the next two moves
# function stop, select model from save
# socket dictionary at the beginning