# UAH Parking Dashboard - Flask Version

A Flask web application that displays real-time parking lot availability for the UAH campus.

## What Changed from JavaScript Version

- **Backend**: Moved from client-side JavaScript data generation to Flask server
- **API**: Added `/api/parking-data` endpoint that serves parking data as JSON
- **Architecture**: Now follows proper client-server pattern
- **Data**: Parking lot data is now served from the backend and can be easily modified

## Project Structure

```
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # HTML template (replaces old index.html)
├── lot_data.json         # Parking lot configuration data
├── requirements.txt      # Python dependencies
└── json_generate.py      # Legacy script (can be removed)
```

## Installation & Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Flask application:**
   ```bash
   python app.py
   ```

3. **Open your browser and go to:**
   ```
   http://127.0.0.1:5000
   ```

## How It Works

### Backend (app.py)
- Loads parking lot data from `lot_data.json`
- Generates random occupancy data for each lot
- Calculates availability, percentages, and status
- Serves data via REST API at `/api/parking-data`
- Serves the HTML dashboard at the root route `/`

### Frontend (templates/index.html)
- Fetches data from Flask API every 10 seconds
- Displays parking lot cards with occupancy progress bars
- Shows summary statistics (total lots, available spots, capacity)
- Maintains the same visual design as the original

### API Response Format
```json
{
  "lots": [
    {
      "lot": "W27",
      "name": "West Lot 27", 
      "capacity": 300,
      "occupancy": 245,
      "available": 55,
      "occupancy_pct": 82,
      "status": "busy"
    }
  ],
  "summary": {
    "total_lots": 6,
    "total_available": 234,
    "total_capacity": 1340,
    "last_updated": "14:30:25"
  }
}
```

## Development

- Flask runs in debug mode by default
- Changes to Python code will auto-reload the server
- Press Ctrl+R in the browser to manually refresh data
- Modify `lot_data.json` to change parking lot configuration

## Next Steps

You could extend this by:
- Adding a database to store historical parking data
- Creating user authentication for admin features
- Adding real parking sensors integration
- Building a REST API for mobile apps
- Adding email/SMS alerts for lot availability