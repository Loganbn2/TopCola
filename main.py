from flask import Flask, jsonify
from datetime import datetime  # Import datetime module

app = Flask(__name__)

from flask_cors import CORS
CORS(app)

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Hello from the backend!"})

@app.route('/api/datetime', methods=['GET'])
def get_datetime():
    # Function to get the current date and time
    now = datetime.now()
    return jsonify({"current_datetime": now.strftime("%Y-%m-%d %H:%M:%S")})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)