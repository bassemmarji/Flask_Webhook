#Flask imports
from flask import render_template, request,session
from flask_socketio import join_room
from init_consumer import app, socketio
import json
import uuid

#Render the assigned template file
@app.route("/", methods=['GET'])
def index():
    return render_template('consumer.html')

# Sending Message through the websocket
def send_message(event, namespace, room, message):
    # print("Message = ", message)
    socketio.emit(event, message, namespace=namespace, room=room)

# Registers a function to be run before the first request to this instance of the application
# Create a unique session ID and store it within the application configuration file
@app.before_first_request
def initialize_params():
    if not hasattr(app.config,'uid'):
        sid = str(uuid.uuid4())
        app.config['uid'] = sid
        print("initialize_params - Session ID stored =", sid)

# Receive the webhooks and emit websocket events
@app.route('/consumetasks', methods=['POST'])
def consumetasks():
    if request.method == 'POST':
        data = request.json
        if data:
           print("Received Data = ", data)
           roomid =  app.config['uid']
           var = json.dumps(data)
           send_message(event='msg', namespace='/collectHooks', room=roomid, message=var)
    return 'OK'

#Execute on connecting
@socketio.on('connect', namespace='/collectHooks')
def socket_connect():
    # Display message upon connecting to the namespace
    print('Client Connected To NameSpace /collectHooks - ', request.sid)

#Execute on disconnecting
@socketio.on('disconnect', namespace='/collectHooks')
def socket_connect():
    # Display message upon disconnecting from the namespace
    print('Client disconnected From NameSpace /collectHooks - ', request.sid)

#Execute upon joining a specific room
@socketio.on('join_room', namespace='/collectHooks')
def on_room():
    if app.config['uid']:
        room = str(app.config['uid'])
        # Display message upon joining a room specific to the session previously stored.
        print(f"Socket joining room {room}")
        join_room(room)

#Execute upon encountering any error related to the websocket
@socketio.on_error_default
def error_handler(e):
    # Display message on error.
    print(f"socket error: {e}, {str(request.event)}")

#Run using port 5001
if __name__ == "__main__":
    socketio.run(app,host='localhost', port=5001,debug=True)