import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Server-side counters for sequences and live active queues
token_sequences = {"CSH": 1, "ACC": 1, "LON": 1, "AMN": 1}
current_queues = {"CSH": 0, "ACC": 0, "LON": 0, "AMN": 0}

@app.route('/')
def home():
    # Renders the frontend HTML page
    return render_template('index.html')

@app.route('/api/generate-token', methods=['POST'])
def generate_token():
    data = request.get_json()
    if not data or 'prefix' not in data or 'service_name' not in data:
        return jsonify({"error": "Invalid request payload"}), 400
    
    prefix = data['prefix']
    service_name = data['service_name']
    
    if prefix not in token_sequences:
        return jsonify({"error": "Invalid service prefix"}), 400
    
    # 1. Fetch and increment current category sequence
    seq_num = token_sequences[prefix]
    formatted_num = f"{seq_num:03d}"  # Pads with zeros (e.g., 001, 002)
    full_token = f"{prefix}-{formatted_num}"
    token_sequences[prefix] += 1
    
    # 2. Increment live waiting metrics
    current_queues[prefix] += 1
    
    # 3. Create real-time operational timestamp
    now = datetime.now()
    time_string = f"Issued on: {now.strftime('%d/%m/%Y')} at {now.strftime('%I:%M:%S %p')}"
    
    return jsonify({
        "token_number": full_token,
        "service_type": f"Department: {service_name}",
        "time_string": time_string,
        "metrics": {
            "CSH": current_queues["CSH"],
            "ACC": current_queues["ACC"],
            "LON": current_queues["LON"],
            "AMN": current_queues["AMN"],
            "total": sum(current_queues.values())
        }
    }), 200

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    # Fetch current state for active dashboards
    return jsonify({
        "CSH": current_queues["CSH"],
        "ACC": current_queues["ACC"],
        "LON": current_queues["LON"],
        "AMN": current_queues["AMN"],
        "total": sum(current_queues.values())
    }), 200

if __name__ == '__main__':
    # Runs the local development server
    app.run(debug=True, port=5002)
