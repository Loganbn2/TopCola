from flask import Flask, jsonify, render_template, request 
from supabase import create_client, Client
import logging 
import os
from flask_cors import CORS
import time
import requests
import threading
from product_data import get_product_info, get_product_ids_by_tag

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

# w
last_seen_id = None
last_seen_id_weighted = None
last_seen_id_tag = None

def product_to_wordpress(title, content, product_name=None, post_id=None, iframe_html=None):
    # Generate slug if product_name and post_id are provided
    slug = None
    if product_name and post_id:
        slug = f"{product_name}-{post_id}".replace(" ", "-").lower()
    # Format title: replace '-' with ' ' and capitalize each word
    formatted_title = title.replace('-', ' ').title()
    post_data = {
        "title": formatted_title,
        "content": content,
        "status": "publish"
    }
    if slug:
        post_data["slug"] = slug
    if iframe_html:
        post_data["meta"] = {"iframe_embed": iframe_html}
    response = requests.post(
        WP_POSTS,
        auth=(wp_username, wp_password),
        json=post_data
    )
    if response.status_code == 201:
        print("✅ WordPress post created:", formatted_title)
        wp_post_id = response.json().get("id")
        # Update Supabase: set published=True and wp_post_id=<WP Post ID>
        try:
            supabase.table("products") \
                .update({"published": True, "wp_post_id": wp_post_id}) \
                .eq("id", post_id) \
                .execute()
            print(f"📝 Updated Supabase for product {post_id} with WP Post ID {wp_post_id}")
        except Exception as e:
            print(f"❌ Failed to update Supabase with WP Post ID for product {post_id}: {str(e)}")
        return True
    else:
        print("❌ Failed to create post:", response.status_code, response.text)
        return False

def mark_post_as_published(post_id):
    print(f"🔍 Trying to mark post ID {post_id} as published")

    try:
        response = supabase.table("products")\
            .update({"published": True})\
            .eq("id", post_id)\
            .eq("published", False)\
            .execute()
        print("🔁 Update response:", response.data)
    except Exception as e:
        print(f"❌ Failed to mark row {post_id} as published:", str(e))

def tag_to_wordpress(title, content, name=None, iframe_html=None):
    # Generate slug if name is provided
    slug = None
    if name:
        slug = f"{name}".replace(" ", "-").lower()
    # Format title: replace '-' with ' ' and capitalize each word
    formatted_title = title.replace('-', ' ').title()
    post_data = {
        "title": formatted_title,
        "content": content,
        "status": "publish"
    }
    if slug:
        post_data["slug"] = slug
    if iframe_html:
        post_data["meta"] = {"iframe_embed": iframe_html}
    response = requests.post(
        WP_POSTS,
        auth=(wp_username, wp_password),
        json=post_data
    )
    if response.status_code == 201:
        print("✅ WordPress tag post created:", formatted_title)
        return True
    else:
        print("❌ Failed to create tag post:", response.status_code, response.text)
        return False

def poll_products():
    global last_seen_id
    while True:
        try:
            # Fetch unpublished posts
            response = supabase.table("products")\
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
            title = row.get("product_name", "Untitled Post")
            content = str(row.get("id", ""))
            product_name = row.get("product_name", "")
            iframe_html = row.get("iframe_html", None)

            if post_id != last_seen_id:
                print("🆕 New post detected (id={}): {}".format(post_id, title))
                success = product_to_wordpress(title, content, product_name, post_id, iframe_html)

                if success:
                    mark_post_as_published(post_id)
                    last_seen_id = post_id

            time.sleep(30)  # Poll every 30 seconds

        except Exception as e:
            print("⚠️ Error in polling:", str(e))
            time.sleep(60)

def poll_weighted_products():
    global last_seen_id_weighted
    while True:
        try:
            response = supabase.table("weighted_products")\
                .select("*")\
                .eq("published", False)\
                .order("id", desc=True)\
                .limit(1)\
                .execute()

            if response.data:
                row = response.data[0]
                if row.get("published") is True:
                    print(f"🚫 Weighted Row {row['id']} already published — skipping.")
                    time.sleep(10)
                    return

            post_id = row["id"]
            title = row.get("product_name", "Untitled Post")
            content = str(row.get("id", ""))
            product_name = row.get("product_name", "")
            iframe_html = row.get("iframe_html", None)

            if post_id != globals().get('last_seen_id_weighted', None):
                print("🆕 New weighted product detected (id={}): {}".format(post_id, title))
                success = product_to_wordpress(title, content, product_name, post_id, iframe_html)

                if success:
                    try:
                        response = supabase.table("weighted_products")\
                            .update({"published": True})\
                            .eq("id", post_id)\
                            .eq("published", False)\
                            .execute()
                        print("🔁 Weighted update response:", response.data)
                    except Exception as e:
                        print(f"❌ Failed to mark weighted row {post_id} as published:", str(e))
                    globals()['last_seen_id_weighted'] = post_id

            time.sleep(30)

        except Exception as e:
            print("⚠️ Error in weighted polling:", str(e))
            time.sleep(60)

def poll_tags():
    global last_seen_id_tag
    while True:
        try:
            response = supabase.table("tags")\
                .select("*")\
                .eq("published", False)\
                .order("id", desc=True)\
                .limit(1)\
                .execute()

            if response.data:
                row = response.data[0]
                if row.get("published") is True:
                    print(f"🚫 Tag Row {row['id']} already published — skipping.")
                    time.sleep(10)
                    return

            post_id = row["id"]
            title = row.get("name", "Untitled Tag")
            content = str(row.get("id", ""))
            name = row.get("name", "")
            iframe_html = row.get("iframe_html", None)

            if post_id != globals().get('last_seen_id_tag', None):
                print("🆕 New tag detected (id={}): {}".format(post_id, title))
                success = tag_to_wordpress(title, content, name, iframe_html)

                if success:
                    try:
                        response = supabase.table("tags")\
                            .update({"published": True})\
                            .eq("id", post_id)\
                            .eq("published", False)\
                            .execute()
                        print("🔁 Tag update response:", response.data)
                    except Exception as e:
                        print(f"❌ Failed to mark tag row {post_id} as published:", str(e))
                    globals()['last_seen_id_tag'] = post_id

            time.sleep(30)

        except Exception as e:
            print("⚠️ Error in tag polling:", str(e))
            time.sleep(60)

def start_polling():
    poll_thread = threading.Thread(target=poll_products, daemon=True)
    poll_thread.start()
    weighted_thread = threading.Thread(target=poll_weighted_products, daemon=True)
    weighted_thread.start()
    tag_thread = threading.Thread(target=poll_tags, daemon=True)
    tag_thread.start()
    return poll_thread, weighted_thread, tag_thread

if __name__ == "__main__":
    # Starts polling immediately when run directly
    start_polling()
    # Keep the main thread alive
    while True:
        time.sleep(3600)