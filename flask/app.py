from flask import Flask, render_template,request,session
from flask_socketio import SocketIO, send,emit,join_room, leave_room, ConnectionRefusedError
import uuid
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app,logger=True, engineio_logger=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
db = SQLAlchemy(app)
socketio = SocketIO(app)

db.session.execute('CREATE TABLE IF NOT EXISTS user ( \
                email TEXT email NOT NULL UNIQUE, username TEXT)')
db.session.execute('CREATE TABLE IF NOT EXISTS room ( \
                roomname TEXT, key TEXT, email NOT NULL UNIQUE)')
db.session.commit()

_email={}
@app.route('/<string:username>/<string:email>')
def index(username,email):
    user=username
    _email["email"]=email
    # email="arpa"
    db.engine.execute("INSERT INTO user (email,username) VALUES(?,?)",(email,user))
    p=db.engine.execute("SELECT * FROM user ").fetchall()
    print(p)
    db.session.commit()
    session["username"]=username
    return render_template('session.html',user=username)

@socketio.on('my event')
def test_message(message):
    emit('my response', {'data': message['data']})

# @socketio.on('my broadcast event')
# def test_message(message):
#     emit('my response', {'data': message['data']}, broadcast=True)

@app.route("/chat")
def chat():
    return render_template("chat.html")

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
    db.engine.execute("INSERT INTO room (roomname,key,email) VALUES(?,?,?)",(roomname,_id,_email["email"]))
    db.session.commit()
    print(roomname,roomID)
    room = _id
    join_room(room)
    emit('private_room',{'roomID':room, "roomname":roomname,'username':session['username']}, room=room)
    # send(username + ' has entered the room.'+room, to=room)




@socketio.on('join')
def join(msg):
    roomname = msg['roomname']
    # roomID["room"]=msg['roomID']
    # print(roomname,roomID)
    _id = msg['roomID']
    print("this s join id:",_id)

    
    # roomID[room].append(request.sid)
    if  roomID.get(roomname) !=_id :
        emit(roomname+" does not exist")
    else:
        db.engine.execute("INSERT INTO room (roomname,key,email) VALUES(?,?,?)",(roomname,_id,_email["email"]))
        db.session.commit()

        key_session[request.sid]=_id
        join_room(_id)
        print("ID check",request.sid,"/n",key_session[request.sid])
        emit('chat',{'data':roomname, "user":_id}, room=_id)
        # send(username + ' has entered the room.'+room, to=room)


@socketio.on('my broadcast event')
def test_message(message):
    # room = message['room']
    print("here is the room",roomID)
    key=db.engine.execute("SELECT key FROM room WHERE email=?",(_email['email'])).fetchone()
    db.session.commit()
    print(key[0])
    emit('chat', {'data': message['data'],"user":session['username']},room=key[0])
    # emit('chat', {'data': message['data'],"user":session['username']},room=key_session[request.sid])


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
    emit('my response', {'data': 'DisConnected'})

if __name__ == '__main__':
    socketio.run(app)