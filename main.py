from flask import Flask, jsonify, render_template  # Ensure Flask imports are included
from datetime import datetime  # Import datetime module
from supabase import create_client, Client  # Ensure Supabase client is imported
import logging  # Import logging module
import os  # Import os for environment variables if needed

# Initialize Flask app
app = Flask(__name__)

# Initialize Supabase client
SUPABASE_URL = "https://otnrvaybkwsvzxgwfhfc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im90bnJ2YXlia3dzdnp4Z3dmaGZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY3MjYwMDIsImV4cCI6MjA2MjMwMjAwMn0.Ox3qDjoX-x-Tcol96i1XQRuqRWr8oUkc_Z-pZaBJTww"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route("/")
def product_list():
    # Fetch data from Supabase
    try:
        response = supabase.table("products").select("*").execute()
        products = response.data if response.data else []
        logging.debug(f"Fetched products: {products}")
    except Exception as e:
        logging.error(f"Error fetching products: {e}")
        products = []

    # Mock data for testing if no products are available
    if not products:
        products = [
            {"name": "Sample Product 1", "price": 10.99},
            {"name": "Sample Product 2", "price": 15.49},
        ]
        logging.debug("Using mock data for products.")

    # Render HTML template with dynamic data
    return render_template("product_list.html", products=products)

@app.route("/test-data")
def test_data():
    # Test route to verify data being sent to the front end
    response = supabase.table("products").select("*").execute()
    return jsonify(response.data if response.data else {"error": "No data found"})

if __name__ == "__main__":
    app.run(debug=True)

