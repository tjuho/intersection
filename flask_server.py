import json
from flask import Flask, jsonify
from simulation import DummylightsTwoCrossings  # Your simulation file

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return super().default(obj)

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

@app.route('/api/simulation')
def get_simulation_data():
    simulation = DummylightsTwoCrossings()
    # Provide some simulation data (e.g., car locations, traffic lights, etc.)
    data = {
        'cars': simulation.world.getCarsLocationsAndDirections(),
        'traffic_lights': simulation.world.getTrafficlightsLocationsAndDirections(),
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)