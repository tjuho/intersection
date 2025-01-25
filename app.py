import json
from flask import Flask, jsonify
from simulation import DummylightsTwoCrossings  # Your simulation file
from trafficlight import Trafficlight
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return super().default(obj)

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

simulation = DummylightsTwoCrossings()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# @app.route('/api/simulation')
# def get_simulation_data():
#     return jsonify(simulation.to_dict())

@app.route('/api/simulation', methods=['GET'])
def get_simulation_data():
    simulation = DummylightsTwoCrossings()  # Replace with your actual method to get the simulation
    simulation_dict = simulation.to_dict()

    # Temporary debugging
    import pprint
    pprint.pprint(simulation_dict)

    return jsonify(simulation_dict)

# @app.route('/api/simulation')
# def get_simulation_data():
#     traffic_light = {
#         "color": "green",
#         "timeToNextColorChange": None,
#         "yellowTime": 1,
#         "redToGreenDelay": 1
#     }
#     return jsonify(traffic_light)
# @app.route('/api/simulation')
# def get_simulation_data():
#     simulation = DummylightsTwoCrossings()
#     # Provide some simulation data (e.g., car locations, traffic lights, etc.)
#     data = {
#         'cars': simulation.world.getCarsLocationsAndDirections(),
#         'traffic_lights': simulation.world.getTrafficlightsLocationsAndDirections(),
#     }
#     return jsonify(data)

# @app.route('/api/simulation', methods=['GET'])
# def get_simulation_data():
#     # Example: Assuming `traffic_lights` is a list of Trafficlight objects
#     traffic_lights = [Trafficlight("green", 1, 1), Trafficlight("red", 1, 1)]
#
#     # Convert each Trafficlight object to a dictionary
#     data = [light.to_dict() for light in traffic_lights]
#
#     return jsonify(data)
