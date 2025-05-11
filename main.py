from flask import Flask, jsonify, render_template  # Ensure Flask imports are included
from supabase import create_client, Client  # Ensure Supabase client is imported
import logging  # Import logging module
import os  # Import os for environment variables if needed
from flask_cors import CORS  # Import CORS
import time
import requests
import threading


# CORS Configuration
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Supabase Configuration
import os
from supabase import create_client, Client

url="https://otnrvaybkwsvzxgwfhfc.supabase.co"
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im90bnJ2YXlia3dzdnp4Z3dmaGZjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjcyNjAwMiwiZXhwIjoyMDYyMzAyMDAyfQ.yu6OmOqNGqkeBwq00tKvZGU0gNdTY3c9c7u4dSeaGBg"
supabase: Client = create_client(url, key)

# WordPress API Configuration
wp_base = "https://topcoladelivery.com/wp-json/wp/v2/"
wp_username = "Logan"
wp_password = "kEET N0me NIpe eBSr y2pC KH7P"

WP_POSTS = f"{wp_base}posts"

'''
# Supabase Polling Configuration
last_seen_id = None

def post_to_wordpress(title, content):
    response = requests.post(
        WP_POSTS,
        auth=(wp_username, wp_password),
        json={
            "title": title,
            "content": content,
            "status": "publish"
        }
    )
    if response.status_code == 201:
        print("✅ WordPress post created:", title)
        return True
    else:
        print("❌ Failed to create post:", response.status_code, response.text)
        return False

def mark_post_as_published(post_id):
    print(f"🔍 Trying to mark post ID {post_id} as published")

    try:
        response = supabase.table("Products")\
            .update({"published": True})\
            .eq("id", post_id)\
            .eq("published", False)\
            .execute()
        print("🔁 Update response:", response.data)
    except Exception as e:
        print(f"❌ Failed to mark row {post_id} as published:", str(e))

def poll_supabase():
    global last_seen_id
    while True:
        try:
            # Fetch unpublished posts
            response = supabase.table("Products")\
                .select("*")\
                .eq("published", False)\
                .order("id", desc=True)\
                .limit(1)\
                .execute()

            if response.data:
                row = response.data[0]
                if row.get("published") is True:
                    print(f"🚫 Row {row['id']} already published — skipping.")
                    time.sleep(10)
                    return

            post_id = row["id"]
            title = row.get("Product Name", "Untitled Post")
            content = str(row.get("id", ""))

            if post_id != last_seen_id:
                print("🆕 New post detected (id={}): {}".format(post_id, title))
                success = post_to_wordpress(title, content)

                if success:
                    mark_post_as_published(post_id)
                    last_seen_id = post_id


            time.sleep(300)  # Poll every 30 seconds

        except Exception as e:
            print("⚠️ Error in polling:", str(e))
            time.sleep(60)

# Starts polling immediately
poll_thread = threading.Thread(target=poll_supabase, daemon=True)
poll_thread.start()
'''

# product_list.html
@app.route('/products-list', methods=['GET'])
def get_product_list():
    try:
        # Fetch data from the 'products' table
        logging.info("Fetching data from the 'Products' table...")
        response = supabase.table('products').select('"product_name"').execute()
        logging.info(f"Supabase response: {response}")
        
        if response.data:
            products = [item['product_name'] for item in response.data]
            logging.info(f"Products fetched: {products}")
            return render_template('product_list.html', products=products)
        else:
            logging.warning("No products found in the 'Products' table.")
            return render_template('product_list.html', products=[], error="No products found")
    except Exception as e:
        logging.error(f"Error fetching products: {e}")
        return render_template('product_list.html', products=[], error=f"An error occurred: {str(e)}")

@app.route('/product-info/<int:product_id>', methods=['GET'])
def get_product_info(product_id):
    try:
        # Fetch data for the specified product ID from the 'products' table
        logging.info(f"Fetching data for product ID {product_id} from the 'Products' table...")
        response = supabase.table('products').select('*').eq('id', product_id).execute()
        logging.info(f"Supabase response: {response}")
        
        if response.data:
            product_info = response.data[0]  # Assuming only one row is returned
            logging.info(f"Product info fetched: {product_info}")
            return render_template('product_page.html', product=product_info)
        else:
            logging.warning(f"No product found with ID {product_id}.")
            return render_template('product_page.html', product=None, error="Product not found")
    except Exception as e:
        logging.error(f"Error fetching product info for ID {product_id}: {e}")
        return render_template('product_page.html', product=None, error=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Start the Supabase polling loop in a background thread
    # poll_thread = threading.Thread(target=poll_supabase, daemon=True)
    # poll_thread.start()

    # Start the Flask web server
    app.run(debug=True, host='127.0.0.1', port=5000)
