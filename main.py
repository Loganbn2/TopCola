from flask import Flask, jsonify, render_template, request 
from supabase import create_client, Client  
import logging 
import os 
from flask_cors import CORS 
import time
import requests
import threading
from product_data import get_product_info, get_product_ids_by_tag, get_flower_info, get_volume_discounts, get_groups, get_promo_codes
from profits_data import get_order_data
from random import shuffle
from datetime import datetime, timedelta
import polling
from werkzeug.utils import secure_filename
import json
import re


# CORS configuration
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5000", "http://localhost:5000"], "methods": ["GET", "POST", "PUT", "DELETE"], "allow_headers": "*"}})

# supabase configuration
import os
from supabase import create_client, Client

url="https://otnrvaybkwsvzxgwfhfc.supabase.co"
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im90bnJ2YXlia3dzdnp4Z3dmaGZjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjcyNjAwMiwiZXhwIjoyMDYyMzAyMDAyfQ.yu6OmOqNGqkeBwq00tKvZGU0gNdTY3c9c7u4dSeaGBg"
supabase: Client = create_client(url, key)

# wordpress configuration
wp_base = "https://topcoladelivery.com/wp-json/wp/v2/"
wp_username = "Logan"
wp_password = "kEET N0me NIpe eBSr y2pC KH7P"

WP_POSTS = f"{wp_base}posts"

import requests

# Register custom Jinja2 filter for shuffling
@app.template_filter('shuffle')
def shuffle_filter(seq):
    shuffled = list(seq)
    shuffle(shuffled)
    return shuffled

# Register custom Jinja2 filter for regex replacement
@app.template_filter('regex_replace')
def regex_replace_filter(s, find, replace):
    return re.sub(find, replace, s)

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

# place order
@app.route('/api/place-order', methods=['POST'])
def place_order():
    try:
        # Parse request data
        data = request.json
        full_name = data.get('fullName', '')
        email = data.get('email', '')
        phone = data.get('phone', '')
        address = data.get('address', '')
        city = data.get('city', '')
        state = data.get('state', '')
        zip_code = data.get('zip', '')
        total = data.get('total', 0.0)
        volume_discounts = data.get('volumeDiscounts', 0.0)
        bxgo_discounts = data.get('bxgoDiscounts', 0.0)
        promo_discounts = data.get('promoDiscounts', 0.0)
        delivery_time = data.get('deliveryTime', '')
        flower_items = data.get('flowerItems', [])  # Get flowerItems array
        product_items = data.get('productItems', [])  # Get productItems array

        # Prepare order data
        order_data = {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "address": address,
            "city": city,
            "state": state,
            "zip": zip_code,
            "total": total,
            "volume_discounts": volume_discounts,
            "BXGO_discounts": bxgo_discounts,
            "promo_discounts": promo_discounts,
            "delivery_time": delivery_time,
            "flower": flower_items,  # Store flowerItems in 'flower' column
            "items": product_items,  # Store productItems in 'items' column
            "created_at": time.strftime('%Y-%m-%d %H:%M:%S')
        }

        # Insert order into Supabase 'orders' table
        response = supabase.table('orders').insert(order_data).execute()

        # Check if the response contains the inserted data
        if response.data and len(response.data) > 0:
            return jsonify({"message": "Order placed successfully", "order_id": response.data[0]['id']}), 201
        else:
            logging.error(f"Error placing order: {response.error}")
            return jsonify({"error": "Failed to place order"}), 500

    except Exception as e:
        logging.error(f"Error in place_order endpoint: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# feature_section.html
@app.route('/feature-section/<string:slug>', methods=['GET'])
def render_feature_section(slug):
    try:
        # Parse the slug into a list of (type, id) tuples
        featured_items = []
        i = 0
        while i < len(slug):
            item_type = slug[i]
            i += 1
            id_str = ''
            while i < len(slug) and slug[i].isdigit():
                id_str += slug[i]
                i += 1
            if not id_str:
                continue
            item_id = int(id_str)
            if item_type == 'f':
                flower_info, flower_error = get_flower_info(supabase, item_id)
                if flower_info:
                    flower_info['type'] = 'flower'
                    featured_items.append(flower_info)
            elif item_type == 'p':
                product_info, product_error = get_product_info(supabase, item_id)
                if product_info:
                    product_info['type'] = 'product'
                    featured_items.append(product_info)
        return render_template(
            'feature_section.html',
            featured_items=featured_items,
            product_error=None,
            flower_error=None
        )
    except Exception as e:
        logging.error(f"Error rendering feature section: {e}")
        return render_template(
            'feature_section.html',
            featured_items=[],
            product_error=f"An error occurred: {str(e)}",
            flower_error=f"An error occurred: {str(e)}"
        )

# profits_reports.html
@app.route('/profits-reports', methods=['GET'])
@app.route('/profits-reports/<int:delta>', methods=['GET'])
def profits_reports(delta=7):
    try:
        orders, error = get_order_data(supabase)
        now = datetime.now()
        cutoff_date = now - timedelta(days=delta)
        return render_template('profits_reports.html', orders=orders, error=error, cutoff_date=cutoff_date, delta=delta)
    except Exception as e:
        logging.error(f"Error rendering profits reports: {e}")
        return render_template('profits_reports.html', orders=[], error=f"An error occurred: {str(e)}", cutoff_date=None, delta=delta)

# admin_inputs.html
@app.route('/admin', methods=['GET'])
def render_admin_inputs():
    try:
        # You can add logic here to fetch data for the admin_inputs page if needed
        return render_template('admin_inputs.html', error=None)
    except Exception as e:
        logging.error(f"Error rendering admin inputs: {e}")
        return render_template('admin_inputs.html', error=f"An error occurred: {str(e)}")


# API endpoint to add a product to the 'products' table
@app.route('/api/add-product', methods=['POST'])
def add_product():
    try:
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            # Handle images and JSON payload
            files = request.files.getlist('images')
            payload = request.form.get('payload')
            if payload:
                data = json.loads(payload)
            else:
                return jsonify({'error': 'Missing product data.'}), 400
        else:
            data = request.json
            files = []

        product_name = data.get('product_name', '')
        price = data.get('price', 0.0)
        cost = data.get('cost', 0.0)
        description = data.get('description', None)
        original_price = data.get('original_price', None)
        group = data.get('group', None)
        tags = data.get('tags', None)
        options = data.get('options', None)

        if not product_name or price is None or cost is None:
            return jsonify({'error': 'Missing required fields.'}), 400

        # Upload images to Supabase Storage
        image_urls = []
        bucket = request.form.get('bucket', 'product-images') if request.content_type and request.content_type.startswith('multipart/form-data') else 'product-images'
        for file in files:
            filename = secure_filename(file.filename)
            # Ensure unique filename by prefixing with timestamp
            unique_filename = f"{int(time.time())}_{filename}"
            file_data = file.read()
            storage_response = supabase.storage.from_(bucket).upload(unique_filename, file_data, {'content-type': file.mimetype})
            if hasattr(storage_response, 'error') and storage_response.error:
                logging.error(f"Error uploading image: {storage_response.error}")
                continue
            image_url = f"{unique_filename}"
            image_urls.append(image_url)

        product_data = {
            'product_name': product_name,
            'price': price,
            'cost': cost,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        if description is not None:
            product_data['description'] = description
        if original_price is not None:
            product_data['original_price'] = original_price
        if group:
            product_data['group'] = group
        if tags is not None:
            product_data['tags'] = tags
        if options is not None:
            product_data['options'] = options
        if image_urls:
            product_data['images'] = image_urls

        response = supabase.table('products').insert(product_data).execute()
        if response.data and len(response.data) > 0:
            return jsonify({'message': 'Product added successfully', 'product_id': response.data[0]['id']}), 201
        else:
            # Check for foreign key violation on group
            error_str = str(response.error) if response.error else ''
            if (
                'violates foreign key constraint' in error_str and 'products_group_fkey' in error_str
            ) or (
                'Key (group)' in error_str and 'is not present in table "groups"' in error_str
            ):
                return jsonify({'error': 'Group does not exist.'}), 400
            logging.error(f"Error adding product: {response.error}")
            return jsonify({'error': 'Failed to add product'}), 500
    except Exception as e:
        logging.error(f"Error in add_product endpoint: {e}")
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500

# API endpoint to add a weighted product to the 'weighted_products' table
@app.route('/api/add-weighted-product', methods=['POST'])
def add_weighted_product():
    try:
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            files = request.files.getlist('images')
            payload = request.form.get('payload')
            if payload:
                data = json.loads(payload)
            else:
                return jsonify({'error': 'Missing product data.'}), 400
        else:
            data = request.json
            files = []

        product_name = data.get('product_name', '')
        price = data.get('price', 0.0)
        cost = data.get('cost', 0.0)
        description = data.get('description', None)
        tags = data.get('tags', None)
        price_tier = data.get('price_tier', None)

        if not product_name or price is None or cost is None or price_tier is None:
            return jsonify({'error': 'Missing required fields.'}), 400

        # Upload images to Supabase Storage
        image_urls = []
        for file in files:
            filename = secure_filename(file.filename)
            # Ensure unique filename by prefixing with timestamp
            unique_filename = f"{int(time.time())}_{filename}"
            file_data = file.read()
            storage_response = supabase.storage.from_('weighted-product-images').upload(unique_filename, file_data, {'content-type': file.mimetype})
            if hasattr(storage_response, 'error') and storage_response.error:
                logging.error(f"Error uploading image: {storage_response.error}")
                continue
            image_url = f"{unique_filename}"
            image_urls.append(image_url)

        weighted_product_data = {
            'product_name': product_name,
            'price/g': price,  # Store as price/g
            'cost/g': cost,    # Store as cost/g
            'price_tier': price_tier,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        if description is not None:
            weighted_product_data['description'] = description
        if tags is not None:
            weighted_product_data['tags'] = tags
        if image_urls:
            weighted_product_data['images'] = image_urls

        response = supabase.table('weighted_products').insert(weighted_product_data).execute()
        if response.data and len(response.data) > 0:
            return jsonify({'message': 'Weighted product added successfully', 'product_id': response.data[0]['id']}), 201
        else:
            logging.error(f"Error adding weighted product: {response.error}")
            return jsonify({'error': 'Failed to add weighted product'}), 500
    except Exception as e:
        logging.error(f"Error in add_weighted_product endpoint: {e}")
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500

# API endpoint to add a tag to the 'tag' table
@app.route('/api/add-tag', methods=['POST'])
def add_tag():
    try:
        data = request.json
        name = data.get('name', '').strip() if data else ''
        if not name:
            return jsonify({'error': 'Tag name is required.'}), 400
        response = supabase.table('tags').insert({'name': name}).execute()
        if response.data and len(response.data) > 0:
            return jsonify({'message': 'Tag added successfully', 'tag_id': response.data[0]['id']}), 201
        else:
            error_str = str(response.error) if response.error else ''
            if 'duplicate key value' in error_str or 'already exists' in error_str:
                return jsonify({'error': 'Tag already exists.'}), 400
            return jsonify({'error': 'Failed to add tag.'}), 500
    except Exception as e:
        logging.error(f"Error in add_tag endpoint: {e}")
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500

# API endpoint to add a promo code to the 'promo_codes' table
@app.route('/api/add-promo-code', methods=['POST'])
def add_promo_code():
    try:
        data = request.json
        code = data.get('code', '').strip() if data else ''
        dollars_off = data.get('dollars_off', None)
        percent_off = data.get('percent_off', None)
        if not code:
            return jsonify({'error': 'Promo code is required.'}), 400
        insert_data = {'code': code}
        if dollars_off is not None:
            insert_data['dollars_off'] = dollars_off
        if percent_off is not None:
            insert_data['percent_off'] = percent_off
        response = supabase.table('promo_codes').insert(insert_data).execute()
        if response.data and len(response.data) > 0:
            # Defensive: return the first key if 'id' is not present
            inserted = response.data[0]
            promo_code_id = inserted.get('id') or next(iter(inserted.values()), None)
            return jsonify({'message': 'Promo code added successfully', 'promo_code_id': promo_code_id}), 201
        else:
            error_str = str(response.error) if response.error else ''
            if 'duplicate key value' in error_str or 'already exists' in error_str:
                return jsonify({'error': 'Promo code already exists.'}), 400
            return jsonify({'error': 'Failed to add promo code.'}), 500
    except Exception as e:
        logging.error(f"Error in add_promo_code endpoint: {e}")
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500

# API endpoint to add a group to the 'groups' table
@app.route('/api/add-bxgo-group', methods=['POST'])
def add_bxgo_group():
    try:
        data = request.json
        group = data.get('group', '').strip() if data else ''
        BOGO = bool(data.get('BOGO', False))
        B2GO = bool(data.get('B2GO', False))
        B3GO = bool(data.get('B3GO', False))
        if not group:
            return jsonify({'error': 'Group name is required.'}), 400
        insert_data = {'group': group, 'BOGO': BOGO, 'B2GO': B2GO, 'B3GO': B3GO}
        response = supabase.table('groups').insert(insert_data).execute()
        if response.data and len(response.data) > 0:
            inserted = response.data[0]
            group_id = inserted.get('id') or next(iter(inserted.values()), None)
            return jsonify({'message': 'Group added successfully', 'group_id': group_id}), 201
        else:
            error_str = str(response.error) if response.error else ''
            if 'duplicate key value' in error_str or 'already exists' in error_str:
                return jsonify({'error': 'Group already exists.'}), 400
            return jsonify({'error': 'Failed to add group.'}), 500
    except Exception as e:
        logging.error(f"Error in add_bxgo_group endpoint: {e}")
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500

# API endpoint to add a flower price tier to the 'volume_discounts' table
@app.route('/api/add-flower-price-tier', methods=['POST'])
def add_flower_price_tier():
    try:
        data = request.json
        tier = data.get('tier', None)
        discount_4g = data.get('4g_discount', None)
        discount_7g = data.get('7g_discount', None)
        discount_14g = data.get('14g_discount', None)
        discount_28g = data.get('28g_discount', None)
        if tier is None:
            return jsonify({'error': 'Tier is required.'}), 400
        insert_data = {'tier': tier}
        if discount_4g is not None:
            insert_data['4g_discount'] = discount_4g
        if discount_7g is not None:
            insert_data['7g_discount'] = discount_7g
        if discount_14g is not None:
            insert_data['14g_discount'] = discount_14g
        if discount_28g is not None:
            insert_data['28g_discount'] = discount_28g
        response = supabase.table('volume_discounts').insert(insert_data).execute()
        if response.data and len(response.data) > 0:
            inserted = response.data[0]
            tier_id = inserted.get('id') or next(iter(inserted.values()), None)
            return jsonify({'message': 'Flower price tier added successfully', 'tier_id': tier_id}), 201
        else:
            error_str = str(response.error) if response.error else ''
            if 'duplicate key value' in error_str or 'already exists' in error_str:
                return jsonify({'error': 'Tier already exists.'}), 400
            return jsonify({'error': 'Failed to add flower price tier.'}), 500
    except Exception as e:
        logging.error(f"Error in add_flower_price_tier endpoint: {e}")
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500

# wordpress configuration
wp_base = "https://topcoladelivery.com/wp-json/wp/v2/"
wp_username = "Logan"
wp_password = "kEET N0me NIpe eBSr y2pC KH7P"

WP_POSTS = f"{wp_base}posts"

def delete_wordpress_post(post_id):
    """
    Delete a WordPress post by its ID.
    Returns True if deleted, False otherwise.
    """
    url = f"{WP_POSTS}/{post_id}?force=true"
    response = requests.delete(url, auth=(wp_username, wp_password))
    if response.status_code == 200 or response.status_code == 410:
        return True
    else:
        print(f"❌ Failed to delete WordPress post {post_id}: {response.status_code} {response.text}")
        return False

from flask import request

@app.route('/api/delete-wp-post', methods=['POST'])
def api_delete_wp_post():
    data = request.get_json()
    post_id = data.get('post_id')
    if not post_id:
        return {"error": "No post_id provided."}, 400
    try:
        success = delete_wordpress_post(post_id)
        if success:
            return {"message": f"Post {post_id} deleted successfully."}
        else:
            return {"error": f"Failed to delete post {post_id}."}, 500
    except Exception as e:
        return {"error": str(e)}, 500

# API endpoint to delete a product and its associated WordPress post
@app.route('/api/delete-product', methods=['POST'])
def delete_product():
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        if not product_id:
            return {"error": "No product_id provided."}, 400
        # Fetch the product from Supabase to get wp_post_id
        response = supabase.table('products').select('wp_post_id').eq('id', product_id).execute()
        if not response.data or len(response.data) == 0:
            return {"error": f"Product with id {product_id} not found."}, 404
        wp_post_id = response.data[0].get('wp_post_id')
        if not wp_post_id:
            return {"error": f"No wp_post_id found for product {product_id}."}, 400
        # Delete the WordPress post
        wp_deleted = delete_wordpress_post(wp_post_id)
        if not wp_deleted:
            return {"error": f"Failed to delete WordPress post {wp_post_id}."}, 500
        # Optionally, delete the product from Supabase
        supabase.table('products').delete().eq('id', product_id).execute()
        return {"message": f"Product {product_id} and WordPress post {wp_post_id} deleted successfully."}
    except Exception as e:
        return {"error": str(e)}, 500

# API endpoint to delete a weighted product and its associated WordPress post
@app.route('/api/delete-weighted-product', methods=['POST'])
def delete_weighted_product():
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        if not product_id:
            return {"error": "No product_id provided."}, 400
        # Fetch the weighted product from Supabase to get wp_post_id
        response = supabase.table('weighted_products').select('wp_post_id').eq('id', product_id).execute()
        if not response.data or len(response.data) == 0:
            return {"error": f"Weighted product with id {product_id} not found."}, 404
        wp_post_id = response.data[0].get('wp_post_id')
        if not wp_post_id:
            return {"error": f"No wp_post_id found for weighted product {product_id}."}, 400
        # Delete the WordPress post
        wp_deleted = delete_wordpress_post(wp_post_id)
        if not wp_deleted:
            return {"error": f"Failed to delete WordPress post {wp_post_id}."}, 500
        # Optionally, delete the weighted product from Supabase
        supabase.table('weighted_products').delete().eq('id', product_id).execute()
        return {"message": f"Weighted product {product_id} and WordPress post {wp_post_id} deleted successfully."}
    except Exception as e:
        return {"error": str(e)}, 500

# run
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
