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
import os
from supabase import create_client, Client

url: str = os.environ.get("https://otnrvaybkwsvzxgwfhfc.supabase.co")
key: str = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im90bnJ2YXlia3dzdnp4Z3dmaGZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY3MjYwMDIsImV4cCI6MjA2MjMwMjAwMn0.Ox3qDjoX-x-Tcol96i1XQRuqRWr8oUkc_Z-pZaBJTww")
supabase: Client = create_client(url, key)

def fetch_supabase_products():
    (supabase.table("Products")
    .select("Product Name")
    .execute()
)

@app.route('/product-list')  # Change the route to match how the template is accessed
def get_product_list():
    value = fetch_supabase_products()  # Dynamically generate the value
    return render_template('product_list.html', value=value)  # Pass value to the template

if __name__ == "__main__":
    #app.run(debug=True, host='0.0.0.0', port=5000)
    app.run(debug=True, host='127.0.0.1', port=5000)



