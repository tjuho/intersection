import json
import traceback
from flask import Flask, jsonify, request
from flask_cors import CORS
from simulation import DummylightsTwoCrossings

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return super().default(obj)

app = Flask(__name__)
CORS(app)
app.json_encoder = CustomJSONEncoder

simulation = DummylightsTwoCrossings()

@app.route('/intersection/api/render-data', methods=['GET'])
def get_render_data():
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))

        cars = [
            {
                "x": x,
                "y": y,
                "direction": d,
                "color": car.color,
                "width": car.width,
                "length": car.length
            }
            for car, x, y, d in simulation.world.getCarsLocationsAndDirections()
        ][offset:offset + limit]

        traffic_lights = [
            {
                "x": x,
                "y": y,
                "direction": d,
                "color": trafficlight.color
            }
            for trafficlight, x, y, d in simulation.world.getTrafficlightsLocationsAndDirections()
        ][offset:offset + limit]

        lanes = [
            {
                "startx": lane.startx,
                "starty": lane.starty,
                "endx": lane.endx,
                "endy": lane.endy,
                "width": lane.width,
                "type": lane.type
            }
            for lane in simulation.world.getLanes()
        ][offset:offset + limit]

        return jsonify({
            "cars": cars,
            "traffic_lights": traffic_lights,
            "lanes": lanes
        })
    except Exception as e:
        app.logger.error(f"Error in get_render_data: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@app.route('/intersection/api/update', methods=['POST'])
def update_simulation():
    try:
        timestep = 0.2
        simulation.moveTimestep(timestep)
        return jsonify({"message": "Simulation updated", "timestep": timestep}), 200
    except Exception as e:
        app.logger.error(f"Error in update_simulation: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@app.route('/intersection/api/test', methods=['GET'])
def test_endpoint():
    return jsonify({"status": "API is working!"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
