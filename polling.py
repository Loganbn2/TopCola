from flask import Flask, jsonify, render_template, request 
from supabase import create_client, Client
import logging 
import os
from flask_cors import CORS
import time
import requests
import threading
from product_data import get_product_info, get_product_ids_by_tag

'''
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