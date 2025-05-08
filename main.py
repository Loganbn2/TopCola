from flask import Flask, jsonify, render_template  # Ensure Flask imports are included
from supabase import create_client, Client  # Ensure Supabase client is imported
import logging  # Import logging module
import os  # Import os for environment variables if needed
import random  # Import random module
from flask_cors import CORS  # Import CORS

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for the Flask app
CORS(app)

# Initialize Supabase client
SUPABASE_URL = "https://otnrvaybkwsvzxgwfhfc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im90bnJ2YXlia3dzdnp4Z3dmaGZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY3MjYwMDIsImV4cCI6MjA2MjMwMjAwMn0.Ox3qDjoX-x-Tcol96i1XQRuqRWr8oUkc_Z-pZaBJTww"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def calculate():
    return random.randint(1, 10)

@app.route('/api/product-value')
def get_product_value():
    value = calculate()  # your logic here
    return jsonify({'value': value})

@app.route('/api/product-list')
def get_product_list():
    value = calculate()  # your logic here
    return render_template('product_list.html', value=value)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)


