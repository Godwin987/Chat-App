from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, send, join_room, leave_room
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)

rooms = {}

def generate_unique_code(Length):
    while True:
        code = ""
        for _ in range(Length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break
    return code 

@app.route('/', methods=['GET', 'POST'])
def home():
    #REDIRECT THE USER TO THE HOME PAGE AND CLEAR THE SESSION
    #TO PREVENT THE USER FROM ACCESSING ANY ROUTES IF THEY'RE NOT IN THE SESSION
    session.clear()

    if  request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        join = request.form.get('join', False)
        create = request.form.get('create', False)

        # A USER HAS TO PROVIDE A NAME
        if not name:
            return render_template('home.html', error='Please enter a name', code=code, name=name)
        
        # CHECK IF A USER IS TRYING TO JOIN A ROOM WITHOUT PROVIDING A ROOM CODE
        if join != False and not code:
            return render_template('home.html', error='Please enter a room code', code=code, name=name)
        
        # CHECK WHAT ROOM THE USER IS TRYING TO ENTER, IF THE ROOM DOESN'T EXIST, GENERATE A ROOM
        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}

        elif code not in rooms:
            return render_template ('home.html', error='Room does not exist.', code=code, name=name)
        
        session['room'] = room
        session['name'] = name

        return redirect(url_for('room'))
    
    return render_template('home.html')

@app.route('/room')
def room():
    room = session.get('room')
    if room is None or session.get('name') is None or room not in rooms:
        return redirect(url_for('home'))
    return render_template("room.html", code=room)

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")


@socketio.on('connect')
def connect(json):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name":name, "message":"Has entered the room"}, to=room)
    rooms[room]["members"] +=1
    print(f"{name} joined room {room}")

@socketio.on('disconnect')
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    
    send({"name":name, "message":"Has left the room"}, to=room)
    print(f"{name} left the room {room}")

if __name__ == '__main__':
    socketio.run(app, debug=True)
