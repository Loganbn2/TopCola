from flask import Flask, jsonify
from datetime import datetime  # Import datetime module
from supabase import create_client, Client  # Import Supabase client

# Initialize Supabase client
SUPABASE_URL = "your_supabase_url"  # Replace with your Supabase URL
SUPABASE_KEY = "your_supabase_key"  # Replace with your Supabase API key
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