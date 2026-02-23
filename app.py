from flask import Flask, jsonify, request
from flask_cors import CORS
from simulator import BuildingSimulator

app = Flask(__name__)
CORS(app)

sim = BuildingSimulator(n_elevators=4, top_floor=20, seed=42)

@app.route('/state', methods=['GET'])
def state():
    return jsonify(sim.get_state())

@app.route('/recommend', methods=['GET'])
def recommend():
    floor = request.args.get('floor', type=int)
    direction = request.args.get('dir', default=None, type=str)
    emergency = request.args.get('emergency', default='false').lower() == 'true'

    if floor is None:
        return jsonify({'error': 'floor query param required'}), 400

    return jsonify(
        sim.recommend(
            request_floor=floor,
            request_direction=direction,
            emergency=emergency
        )
    )

@app.route('/step', methods=['POST'])
def step():
    sim.step_simulation()
    return jsonify(sim.get_state())

@app.route('/set_state', methods=['POST'])
def set_state():
    """
    Body JSON examples:
    { "id": 1, "state": "out_of_service" }
    { "id": 2, "load": 0.7 }
    { "id": 3, "current_floor": 10, "stops": [12,15] }
    """
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({'error': 'id required'}), 400

    eid = int(data['id'])
    elevator = next((e for e in sim.elevators if e.id == eid), None)

    if not elevator:
        return jsonify({'error': 'invalid elevator id'}), 400

    if 'state' in data:
        elevator.state = data['state']
    if 'current_floor' in data:
        elevator.current_floor = int(data['current_floor'])
    if 'stops' in data:
        elevator.stops = list(map(int, data['stops']))
    if 'direction' in data:
        elevator.direction = data['direction']
    if 'load' in data:
        elevator.load = float(data['load'])

    return jsonify({'status': 'ok', 'elevator': elevator.to_dict()})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
