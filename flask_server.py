from flask import Flask, jsonify
from simulation import DummylightsTwoCrossings  # Your simulation file

app = Flask(__name__)

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