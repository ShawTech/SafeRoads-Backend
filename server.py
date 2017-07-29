from json import JSONEncoder

from flask import Flask
from flask_socketio import SocketIO

from flask_cors import CORS

from threading import Event, Thread


class DictEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


# ML data model
class LatLng:
    """Coordinates"""

    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng


class TaheapInput:
    """Inputs into the network"""

    def __init__(self, time, rainfall, latlng):
        self.time = time
        self.rainfall = rainfall
        self.latlng = latlng


class TaheapOutput:
    """Outputs from the network"""

    def __init__(self, latlng, crash_probability):
        self.latlng = latlng
        self.crash_probability = crash_probability


def set_interval(interval, func, *args):
    """
      :param interval: The period between function calls in seconds
      :param func: The function that gets called periodically
      :param args: The arguments to pass into the function
      :return: A function that you can use to stop the tiker
    """
    stopped = Event()

    def loop():
        while not stopped.wait(interval):
            func(*args)

    Thread(target=loop).start()
    return stopped.set


print("Starting server")
# Backend state
heatmap_crash_data = [
    TaheapOutput(LatLng(-37.8136, 144.9631), 0.5)
]

# Flask 
app = Flask(__name__)
CORS(app)

# Socket IO
endpoint_crash_data = 'crash_data'
socketio = SocketIO(app)


@socketio.on('connection')
def on_connect():
    emit_crash_data()


def emit_crash_data():
    print("This is a test")
    socketio.emit(
        endpoint_crash_data,
        {"test": "test"},
      namespace='/'
    )


print("Starting timer")
ticker = set_interval(1, emit_crash_data)

socketio.run(app, port=8080, debug=True)
