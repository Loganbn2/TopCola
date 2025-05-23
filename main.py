from flask import Flask, jsonify, render_template, request 
from supabase import create_client, Client  
import logging 
import os 
from flask_cors import CORS 
import time
import requests
import threading
from product_data import get_product_info, get_product_ids_by_tag, get_flower_info, get_volume_discounts, get_groups
from random import shuffle


# CORS configuration
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5000", "http://localhost:5000"], "methods": ["GET", "POST", "PUT", "DELETE"], "allow_headers": "*"}})

# supabase configuration
import os
from supabase import create_client, Client

url="https://otnrvaybkwsvzxgwfhfc.supabase.co"
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im90bnJ2YXlia3dzdnp4Z3dmaGZjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjcyNjAwMiwiZXhwIjoyMDYyMzAyMDAyfQ.yu6OmOqNGqkeBwq00tKvZGU0gNdTY3c9c7u4dSeaGBg"
supabase: Client = create_client(url, key)

# Register custom Jinja2 filter for shuffling
@app.template_filter('shuffle')
def shuffle_filter(seq):
    shuffled = list(seq)
    shuffle(shuffled)
    return shuffled

# product_list.html
@app.route('/products-list/<string:tag>', methods=['GET'])
def render_products_list(tag):
    try:
        product_ids, flower_ids, error = get_product_ids_by_tag(supabase, tag)

        # Fetch product and flower details
        product_details = [get_product_info(supabase, pid)[0] for pid in product_ids] if product_ids else []
        flower_details = [get_flower_info(supabase, fid)[0] for fid in flower_ids] if flower_ids else []

        return render_template('product_list.html', 
                               product_ids=(product_ids, flower_ids), 
                               product_details=product_details, 
                               flower_details=flower_details, 
                               error=error, 
                               tag=tag)
    except Exception as e:
        logging.error(f"Error rendering products list: {e}")
        return render_template('product_list.html', 
                               product_ids=[], 
                               product_details=[], 
                               flower_details=[], 
                               error=f"An error occurred: {str(e)}", 
                               tag=None)


# product_page.html
@app.route('/product-info/<int:product_id>', methods=['GET'])
def render_product_info(product_id):
    try:
        product_info, error = get_product_info(supabase, product_id)
        return render_template('product_page.html', product=product_info, error=error)
    except Exception as e:
        logging.error(f"Error rendering product info for ID {product_id}: {e}")
        return render_template('product_page.html', product=None, error=f"An error occurred: {str(e)}")
    
# flower_page.html
@app.route('/flower-info/<int:product_id>', methods=['GET'])
def render_flower_info(product_id):
    try:
        product_info, error = get_flower_info(supabase, product_id)
        return render_template('flower_page.html', product=product_info, error=error)
    except Exception as e:
        logging.error(f"Error rendering product info for ID {product_id}: {e}")
        return render_template('flower_page.html', product=None, error=f"An error occurred: {str(e)}")

# cart.html
@app.route('/cart', methods=['GET'])
def render_cart():
    try:
        cart_data = []
        volume_discounts, error = get_volume_discounts(supabase)
        groups, error = get_groups(supabase)
        return render_template('cart.html', cart=cart_data, volume_discounts=volume_discounts, groups=groups, error=error)
    except Exception as e:
        logging.error(f"Error rendering cart: {e}")
        return render_template('cart.html', cart=[], groups=[], volume_discounts=[], error=f"An error occurred: {str(e)}")

# run
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
