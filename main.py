from flask import Flask, jsonify
from flask_cors import CORS
CORS(app)
from datetime import datetime  # Import datetime module

app = Flask(__name__)

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Hello from the backend!"})

@app.route('/api/datetime', methods=['GET'])
def get_datetime():
    # Function to get the current date and time
    now = datetime.now()
    return jsonify({"current_datetime": now.strftime("%Y-%m-%d %H:%M:%S")})

if __name__ == '__main__':
    app.run(debug=True)