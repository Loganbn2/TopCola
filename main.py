from flask import Flask, jsonify, render_template, request 
from supabase import create_client, Client  
import logging 
import os 
from flask_cors import CORS 
import time
import requests
import threading
from product_data import get_product_info, get_product_ids_by_tag, get_flower_info, get_volume_discounts, get_groups, get_promo_codes
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
        promo_codes, error = get_promo_codes(supabase)
        return render_template('cart.html', cart=cart_data, volume_discounts=volume_discounts, groups=groups, promo_codes=promo_codes, error=error)
    except Exception as e:
        logging.error(f"Error rendering cart: {e}")
        return render_template('cart.html', cart=[], groups=[], volume_discounts=[], promo_codes=[], error=f"An error occurred: {str(e)}")

@app.route('/api/place-order', methods=['POST'])
def place_order():
    try:
        # Parse request data
        data = request.json
        product_line_items = data.get('productLineItems', [])
        flower_line_items = data.get('flowerLineItems', [])
        volume_discount = data.get('volumeDiscount', 0)
        buy_x_get_1_discount = data.get('buyXGet1Discount', 0)
        promo_code_discount = data.get('promoCodeDiscount', 0)
        total = data.get('total', 0)
        customer_name = data.get('customerName', '')
        customer_email = data.get('customerEmail', '')
        customer_phone = data.get('customerPhone', '')
        customer_address = data.get('customerAddress', '')
        customer_city = data.get('customerCity', '')
        customer_state = data.get('customerState', '')
        customer_zip = data.get('customerZip', '')
        payment_method = data.get('paymentMethod', '')
        delivery_time = data.get('deliveryTime', '')

        # Prepare order data
        order_data = {
            "product_line_items": product_line_items,
            "flower_line_items": flower_line_items,
            "volume_discount": volume_discount,
            "buy_x_get_1_discount": buy_x_get_1_discount,
            "promo_code_discount": promo_code_discount,
            "total": total,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_phone": customer_phone,
            "customer_address": customer_address,
            "customer_city": customer_city,
            "customer_state": customer_state,
            "customer_zip": customer_zip,
            "payment_method": payment_method,
            "delivery_time": delivery_time,
            "created_at": time.strftime('%Y-%m-%d %H:%M:%S')
        }

        # Insert order into Supabase 'orders' table
        response = supabase.table('orders').insert(order_data).execute()

        if response.get('status_code') == 201:
            return jsonify({"message": "Order placed successfully", "order_id": response.get('data')[0].get('id')}), 201
        else:
            logging.error(f"Error placing order: {response.get('error')}")
            return jsonify({"error": "Failed to place order"}), 500

    except Exception as e:
        logging.error(f"Error in place_order endpoint: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# run
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
