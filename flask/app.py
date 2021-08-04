from flask import Flask, render_template,request,session
from flask_socketio import SocketIO, send,emit,join_room, leave_room, ConnectionRefusedError
import uuid
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app,logger=True, engineio_logger=True)
socketio = SocketIO(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
db = SQLAlchemy(app)


db.session.execute('CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT email NOT NULL UNIQUE, username TEXT)')
db.session.execute('CREATE TABLE IF NOT EXISTS myroom (id INTEGER PRIMARY KEY AUTOINCREMENT, roomname TEXT, key TEXT, email NOT NULL UNIQUE)')
db.session.commit()


@app.route('/<username>')
def home(username):
    return render_template('index.html',user=username)

@app.route("/chat/<string:roomname>/<string:email>")
def generate_room_key(roomname,email):
    roomname=roomname
    email=email
    key=str(uuid.uuid1())
    # print(request.sid)
    db.engine.execute("INSERT INTO myroom (roomname,key,email) VALUES(?,?,?)",(roomname,key,email))
    # print(user,request.sid)
    db.session.commit()
    data={'roomname':roomname,"key":key,"email":email}
    return data
# @app.route('/<username>')
# def index(username):
#     # user=username
#     # session["username"]=username
#     return render_template('session.html',user=username)

@socketio.on('my event')
def test_message(message):
    emit('my response', {'data': message['data']})

# @socketio.on('my broadcast event')
# def test_message(message):
#     emit('my response', {'data': message['data']}, broadcast=True)

_user={}
@app.route("/chat/<user>")
def chat(user):
    _user["user"]=user
    return render_template("chat.html",user=user)

@socketio.on('connect')
def test_connect():
    # if True:
    #     raise ConnectionRefusedError('unauthorized!')
    print("connected",request.sid)
    emit('my response', {'data': 'Connected'})


roomID={}
key_session={}
@socketio.on('create_room')
def create_room(msg):
    roomname = msg['roomname']
    _id=str(uuid.uuid1())
    roomID[roomname]=_id
    # session['username']=msg['username']
    key_session[request.sid]=_id

    print(roomname,roomID)
    room = _id
    join_room(room)
    emit('private_room',{'roomID':room, "roomname":roomname,'username':session['username']},to=room)
    # send(username + ' has entered the room.'+room, to=room)




@socketio.on('join')
def join(msg):
    roomname = msg['roomname']
    _id = msg['roomID']

    try:
        room_and_key=db.engine.execute("SELECT key,roomname,email from myroom where id=?",_id).fetchone()
        key,roomname=room_and_key[0],room_and_key[1]
        join_room(key)
        key_session[request.sid]=_user["user"]
        roomname = f"{_user['user']} has joined the room {msg['roomname']}"
        # roomID["room"]=msg['roomID']
        # print(roomname,roomID)
        print("this s join id:",_id)
        print("ID check",msg['roomID'],"/n",key_session[request.sid])
        emit('join',{'data':roomname, "user":_id}, room=key)
            # send(username + ' has entered the room.'+room, to=room)
    except:
        join_room('404')
        emit('chat',{'data':"Roomname not found 404", "user":"entered id didn't found"}, room='404')
        raise ConnectionRefusedError('unauthorized!')
        emit('disconnect',room='404')


@socketio.on('my broadcast event')
def test_message(message):
    _id = message['room']
    # print("here is the room",roomID["room"])
    # print("here is the user",_user["user"],key_session[request.sid])

    room_and_key=db.engine.execute("SELECT key,roomname,email from myroom where id=?",_id).fetchone()
    key,roomname=room_and_key[0],room_and_key[1]
    # if request.sid in roomID[_id]:
    emit('chat', {'data': message['data'],"user":key_session[request.sid]},room=key)


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
    emit('my response', {'data': 'DisConnected'})

if __name__ == '__main__':
    socketio.run(app,debug=0)