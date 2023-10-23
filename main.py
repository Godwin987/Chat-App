from flask import Flask, render_template, redirect
from flask_socketio import SocketIO

app = Flask("__name__")
app.config['SECRET_KEY'] = "mysecretkeyisnotyourbusinesspleasedon'tdisturbmeiwillnottellyouanything"
socketio = SocketIO(app)


@app.route('/', methods=['GET', 'POST'])
def chat():
    return render_template('chat.html')

def messageReceived():
    print('messaga was received')


if __name__ == "__main__":
    socketio.run(app)
