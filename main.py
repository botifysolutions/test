from flask import Flask, render_template, jsonify, request
import requests
import traceback
import json
from flask_socketio import SocketIO, emit
import eventlet
import threading



api_key = "43b3e8fa557ea6e0805324d87cdcbf9ac63944e4"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, async_mode='eventlet')

# List to store the coordinates of connected users
user_coordinates = []

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():

    print('User connected:', request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print('User disconnected:', request.sid)
    remove_user_coordinates(request.sid)





@app.route('/get_user_location', methods=['POST', 'GET'])
def get_user_location():
    # Get the user's IP address from the request
    ip_address = request.remote_addr


    api_url = f"https://api.db-ip.com/v2/{api_key}/{ip_address}"

    response = requests.get(api_url)
    #print(response)
    if response.status_code == 200:
        result = response.json()
        #print(result["latitude"])

        # Perform your logic to fetch the user's location
        # Assuming you have retrieved the latitude and longitude
        latitude = result["latitude"]
        longitude = result["longitude"]

    # Create a dictionary representing the location data
    location_data = {
        'latitude': latitude,
        'longitude': longitude
    }


    return location_data



@socketio.on('send_coordinates')
def handle_send_coordinates(data):

    coodinates = get_user_location()
    json.dumps(coodinates)
    user_id = request.sid
    latitude = coodinates['latitude']
    longitude = coodinates['longitude']
    
    add_user_coordinates(user_id, latitude, longitude)

def add_user_coordinates(user_id, latitude, longitude):
    user_coordinates.append({
        'user_id': user_id,
        'latitude': latitude,
        'longitude': longitude
    })

def remove_user_coordinates(user_id):
    user_coordinates[:] = [coord for coord in user_coordinates if coord['user_id'] != user_id]

def send_all_coordinates():
    socketio.emit('update_coordinates', user_coordinates, broadcast=True)

if __name__ == '__main__':
    # Start a background task to send all coordinates every 5 seconds
    eventlet.spawn(send_all_coordinates)
    socketio.run(app)
