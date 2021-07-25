from flask import Flask, render_template,request
from flask_socketio import SocketIO, send,emit,join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app,logger=True, engineio_logger=True)

@app.route('/')
def index():
    return render_template('session.html')

@socketio.on('my event')
def test_message(message):
    emit('my response', {'data': message['data']})

# @socketio.on('my broadcast event')
# def test_message(message):
#     emit('my response', {'data': message['data']}, broadcast=True)



@socketio.on('connect')
def test_connect():
    print("connected",request.sid)
    emit('my response', {'data': 'Connected'})

roomD={}
@socketio.on('join')
def join(msg):
    username = msg['username']
    roomD["room"]=msg['room']
    print(username,roomD)
    room = msg['room']
    join_room(room)
    emit('chat',{'data':username, "user":room}, room=room)
    # send(username + ' has entered the room.'+room, to=room)

@socketio.on('my broadcast event')
def test_message(message):
    # room = message['room']
    print("here is the room",roomD)
    emit('chat', {'data': message['data'],"user":request.sid},room=roomD["room"] )


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
    emit('my response', {'data': 'DisConnected'})

if __name__ == '__main__':
    socketio.run(app)