from flask import Flask, render_template, send_from_directory, jsonify
from flask_socketio import SocketIO, emit
import time
import threading
import json
from hack import *
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

def send_coordinates():
    offset = load_offset()
    csgo = load_game()
    engine_base = load_engine_base(csgo)
    client_base = load_client_base(csgo)
    map_name = get_map(csgo, engine_base, offset)


    local_player = get_Local_player(csgo, client_base, offset)

    while True:
        data = {'map_name': map_name}

        players = get_players(csgo, client_base, offset, local_player)

        data['players'] = players

        socketio.emit('message', data)

        time.sleep(0.05)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map/<map_name>')
def get_map_image(map_name):
    return send_from_directory('static/images', f'{map_name}')

@app.route('/map_info/<map_name>')
def get_mapinfo(map_name):
    filename = 'static/map_info/' + f'{map_name}.json'
    print(filename)

    with open(filename) as f:
        data = f.read()
    parsed_data = json.loads(data)

    pos_x = parsed_data["pos_x"]
    pos_y = parsed_data["pos_y"]
    scale = parsed_data["scale"]

    res_data = {
        'pos_x': pos_x,
        'pos_y': pos_y,
        'scale': scale
    }

    return jsonify(res_data)


@socketio.on('connect')
def handle_connect():
    print('WebSocket connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('WebSocket disconnected')


if __name__ == '__main__':

    threading.Thread(target=send_coordinates).start()

    socketio.run(app, host='0.0.0.0', port=8080)