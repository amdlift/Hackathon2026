from flask import Flask, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

lots = {
    "W27": {"name": "West Lot 27",             "capacity": 300},
    "CGP": {"name": "Charger Park Garage",      "capacity": 450},
    "E10": {"name": "East Lot 10",              "capacity": 180},
    "N5":  {"name": "North Lot 5",              "capacity": 120},
    "S14": {"name": "South Engineering Lot",    "capacity": 200},
    "UC3": {"name": "Union Center Lot 3",       "capacity": 90},
}

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