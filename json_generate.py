import json

def generate_json(lot_name: str = "A1", num_spots: int = 100, current: int = 50):
    x = {
        "lot_name": lot_name,
        "max_occupancy": num_spots,
        "current_occupancy": current
    }

    y = json.dumps(x, indent=2)

    print(y)

generate_json("B2", 80, 75)