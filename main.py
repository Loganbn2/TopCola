from flask import Flask, jsonify
from datetime import datetime  # Import datetime module
from supabase import create_client, Client  # Import Supabase client
import random  # Import random module

# Initialize Supabase client
# Replace with your real Supabase credentials
SUPABASE_URL = "https://otnrvaybkwsvzxgwfhfc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im90bnJ2YXlia3dzdnp4Z3dmaGZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY3MjYwMDIsImV4cCI6MjA2MjMwMjAwMn0.Ox3qDjoX-x-Tcol96i1XQRuqRWr8oUkc_Z-pZaBJTww"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

from flask_cors import CORS
CORS(app)

@app.route('https://topcola.onrender.com/api/random-number', methods=['GET'])
def get_random_number():
    return jsonify({"random_number": random.randint(1, 10)})


if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))