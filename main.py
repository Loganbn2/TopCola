from flask import Flask, jsonify, render_template  # Ensure Flask imports are included
from supabase import create_client, Client  # Ensure Supabase client is imported
import logging  # Import logging module
import os  # Import os for environment variables if needed
import random  # Import random module
from flask_cors import CORS  # Import CORS

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for the Flask app
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize Supabase client
import os
from supabase import create_client, Client

url="https://otnrvaybkwsvzxgwfhfc.supabase.co"
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im90bnJ2YXlia3dzdnp4Z3dmaGZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY3MjYwMDIsImV4cCI6MjA2MjMwMjAwMn0.Ox3qDjoX-x-Tcol96i1XQRuqRWr8oUkc_Z-pZaBJTww"
supabase: Client = create_client(url, key)

@app.route('/products', methods=['GET'])
def get_products():
    try:
        # Fetch data from the 'Products' table
        logging.info("Fetching data from the 'Products' table...")
        response = supabase.table('Products').select('"Product Name"').execute()
        logging.info(f"Supabase response: {response}")
        
        if response.data:
            products = [item['Product Name'] for item in response.data]
            logging.info(f"Products fetched: {products}")
            return render_template('product_list.html', products=products)
        else:
            logging.warning("No products found in the 'Products' table.")
            return render_template('product_list.html', products=[], error="No products found")
    except Exception as e:
        logging.error(f"Error fetching products: {e}")
        return render_template('product_list.html', products=[], error=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)