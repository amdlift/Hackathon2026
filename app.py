<<<<<<< Updated upstream
from flask import Flask, jsonify, send_from_directory
import random

app = Flask(__name__)

lots = {
    "W27": {"name": "West Lot 27",          "capacity": 300},
    "CGP": {"name": "Charger Park Garage",   "capacity": 450},
    "E10": {"name": "East Lot 10",           "capacity": 180},
    "N5":  {"name": "North Lot 5",           "capacity": 120},
    "S14": {"name": "South Engineering Lot", "capacity": 200},
    "UC3": {"name": "Union Center Lot 3",    "capacity": 90},
}

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api/lots")
def get_lots():
    result = {}
    for lot_id, lot in lots.items():
        occupancy = random.randint(0, lot["capacity"])
        result[lot_id] = {
            "name": lot["name"],
            "capacity": lot["capacity"],
            "occupancy": occupancy,
            "available": lot["capacity"] - occupancy
        }
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
=======
from flask import Flask, render_template, jsonify
import json
import random
from datetime import datetime

app = Flask(__name__)

# Load parking lot data
def load_parking_data():
    try:
        with open('lot_data.json', 'r') as file:
            data = json.load(file)
        return data['parking_lots']
    except FileNotFoundError:
        # Fallback data if JSON file doesn't exist
        return [
            {"lot": "W27", "name": "West Lot 27", "capacity": 300},
            {"lot": "CGP", "name": "Charger Park Garage", "capacity": 450},
            {"lot": "E10", "name": "East Lot 10", "capacity": 180},
            {"lot": "N5", "name": "North Lot 5", "capacity": 120},
            {"lot": "S14", "name": "South Engineering Lot", "capacity": 200},
            {"lot": "UC3", "name": "Union Center Lot 3", "capacity": 90},
        ]


def generate_occupancy_data():
    """Generate random occupancy data for all parking lots"""
    lots = load_parking_data()
    
    for lot in lots:
        # Generate random occupancy (0 to capacity)
        occupancy = random.randint(0, lot['capacity'])
        available = lot['capacity'] - occupancy
        occupancy_pct = round((occupancy / lot['capacity']) * 100)
        
        # Add calculated fields
        lot['occupancy'] = occupancy
        lot['available'] = available
        lot['occupancy_pct'] = occupancy_pct
        
        # Determine status
        if occupancy_pct >= 100:
            lot['status'] = 'full'
        elif occupancy_pct >= 70:
            lot['status'] = 'busy'
        else:
            lot['status'] = 'open'
    
    return lots

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('index.html')

@app.route('/api/parking-data')
def get_parking_data():
    """API endpoint to get current parking lot data"""
    lots = generate_occupancy_data()
    
    # Calculate summary statistics
    total_lots = len(lots)
    total_available = sum(lot['available'] for lot in lots)
    total_capacity = sum(lot['capacity'] for lot in lots)
    last_updated = datetime.now().strftime('%H:%M:%S')
    
    return jsonify({
        'lots': lots,
        'summary': {
            'total_lots': total_lots,
            'total_available': total_available,
            'total_capacity': total_capacity,
            'last_updated': last_updated
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
>>>>>>> Stashed changes
