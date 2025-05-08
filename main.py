from flask import Flask, jsonify
from datetime import datetime  # Import datetime module
from supabase import create_client, Client  # Import Supabase client

# Initialize Supabase client
# Replace with your real Supabase credentials
SUPABASE_URL = "https://otnrvaybkwsvzxgwfhfc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im90bnJ2YXlia3dzdnp4Z3dmaGZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY3MjYwMDIsImV4cCI6MjA2MjMwMjAwMn0.Ox3qDjoX-x-Tcol96i1XQRuqRWr8oUkc_Z-pZaBJTww"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

from flask_cors import CORS
CORS(app)

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Hello from the backend!"})

@app.route('/api/products', methods=['GET'])
def get_products():
    # Fetch all products from the 'Products' table
    response = supabase.table('Products').select('*').execute()
    if response.error:
        return jsonify({"error": response.error.message}), 500
    return jsonify(response.data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)