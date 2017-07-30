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
    state.heatmap_crash_data = random_uniform_crash_data()

print("Starting server")

# Flask
app = Flask(__name__)
CORS(app)

# State
current_state = BackendState([])


# Routes
@app.route('/crash/probability')
def crash_probability():
    return str(json.dumps([x.json() for x in current_state.heatmap_crash_data]))


@app.route('/crash/probability/test/random')
def crash_probability_random():
    return str(json.dumps([
                              TaheapOutput(
                                  LatLng(
                                      -37.8136 + (random() - 0.5) * 0.1,
                                      144.9631 + (random() - 0.5) * 0.1,
                                  ),
                                  random()
                              ).json() for _ in range(3000)
                          ]))


@app.route('/crash/probability/test/uniform')
def crash_probability_uniform():
    return random_uniform_crash_data()


def create_relative_taheap_output(x, y):
    probability = random()
    count = int(probability * 5)
    return [TaheapOutput(
        LatLng(
            -37.8136 + (-0.5 + x / 100) * 0.1 * (200/66) + (random() - 0.5) * 0.005,
            144.9631 + (-0.5 + y / 100) * 0.1 * (200/66) + (random() - 0.5) * 0.005
        ),
        probability
    ) for _ in range(count)]


def random_uniform_crash_data():
    data = uniform_map_distribution(
        200,
        200,
        create_relative_taheap_output
    )
    return data


def clustered_map_distribution(width, height, generate_output):
    outputs = [None] * (width * height)
    x = 0
    while x < width:
        y = 0
        actual_y = 0
        while y < height:
            sub_outputs = generate_output(x, actual_y)
            point_index = 0
            while point_index < len(sub_outputs) and y < height:
                outputs[x * width + y] = sub_outputs[point_index]
                point_index += 1
                y += 1
                actual_y += 1
        x += 1
    return outputs


def uniform_map_distribution(width, height, generate_output):
    outputs = [None] * (width * height)
    x = 0
    while x < width:
        y = 0
        actual_y = 0
        while y < height:
            sub_outputs = generate_output(x, actual_y)
            point_index = 0
            while point_index < len(sub_outputs) and y < height:
                outputs[x * width + y] = sub_outputs[point_index]
                point_index += 1
                y += 1
            actual_y += 1
        x += 1
    return outputs

recalculate_probabilities(current_state)
# Recalculate probabilities every so often.
set_interval(10, recalculate_probabilities, current_state)

# Now run the server
app.run(port=3141, debug=True)
