import json
from flask import Flask
from flask_cors import CORS

from random import random

from threading import Event, Thread

from random import randint


# ML data model
class LatLng:
    """Coordinates"""

    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

    def json(self):
        return {
            'lat': self.lat,
            'lng': self.lng
        }


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

    def json(self):
        return {
            'latlng': self.latlng.json(),
            'crash_probability': self.crash_probability
        }


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


class BackendState:
    def __init__(self, heatmap_crash_data):
        self.heatmap_crash_data = heatmap_crash_data


def recalculate_probabilities(state):
    state.heatmap_crash_data = \
        [TaheapOutput(LatLng(-37.8136 + random() * 6, 144.9631 - 30 * random()), random()) for _ in range(10000)]


print("Starting server")

# Flask
app = Flask(__name__)
CORS(app)

current_state = BackendState([])


@app.route('/crash/probability')
def crash_probability():
    return str(json.dumps([x.json() for x in current_state.heatmap_crash_data]))

    print("\n\t~~ [!!]: Socket IO connected ~~\n")

set_interval(1, recalculate_probabilities, current_state)

app.run(port=8080, debug=True)
