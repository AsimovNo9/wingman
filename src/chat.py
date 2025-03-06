from flask import Blueprint, render_template
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user, login_required
from . import socketio

chat = Blueprint("chat", __name__)


@chat.route("/chat", methods=['GET', 'POST'])
@login_required
def start_chat():
    return render_template("chat.html", user=current_user)


@socketio.on("join")
def handle_join(data):
    room = data["room"]
    join_room(room)
    emit("message", {"user": "System",
                     "msg": f"{current_user.firstName} joined"}, room=room)


@socketio.on("message")
def handle_message(data):
    room = data["room"]
    msg = data["msg"]
    emit("message", {"user": current_user.firstName, "msg": msg}, room=room)


@socketio.on("leave")
def handle_leave(data):
    room = data["room"]
    leave_room(room)
    emit("message", {"user": "System",
         "msg": f"{current_user.firstName} left."}, room=room)
