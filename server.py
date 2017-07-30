import json
from flask import Flask
from flask_cors import CORS

from random import random

from threading import Event, Thread


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
    state.heatmap_crash_data = [
        TaheapOutput(
            LatLng(
                -37.8136 + (random() - 0.5) * 0.1,
                144.9631 + (random() - 0.5) * 0.1,
            ),
            random()
        ) for _ in range(3000)
        ]


print("Starting server")

# Flask
app = Flask(__name__)
CORS(app)

# State
current_state = BackendState([])


# Routes
@app.route('/crash/probability/')
def crash_probability():
    return crash_probability_uniform()


@app.route('/crash/probability/test/random')
def crash_probability_random():
    return str(json.dumps([
        TaheapOutput(
            LatLng(
                -37.8136 + (random() - 0.5) * 0.1,
                144.9631 + (random() - 0.5) * 0.1,
            ),
            random()
        ) for _ in range(3000)
    ]))


@app.route('/crash/probability/test/uniform')
def crash_probability_uniform():
    return str(json.dumps(uniform_map_distribution(
        55,
        55,
        lambda x, y:
            TaheapOutput(
                LatLng(
                    -37.8136 - 0.5 + x / 55,
                    144.9631 - 0.5 + y / 55
                ),
                random()
            )
    )))


def uniform_map_distribution(width, height, generate_output):
    outputs = [None] * (width * height)
    x = 0
    while x < 55:
        y = 0
        while y < 55:
            outputs[x * 55 + y] = generate_output(x, y)
    return outputs

recalculate_probabilities(current_state)
# Recalculate probabilities every so often.
set_interval(10, recalculate_probabilities, current_state)

# Now run the server
app.run(port=8080, debug=True)
