from flask import render_template
import logging
import json  # Import json for serialization
from datetime import datetime, timedelta

def get_week_report(supabase):
    """
    Fetches the average order total from the last 7 days using a raw SQL query in Supabase.
    Returns the average as a float, or None on error.
    Logs the fetched result to the console.
    """
    try:
        # Supabase Python client does not support raw SQL directly, but you can use an RPC (Postgres function)
        # If you have SQL access enabled, you can use the 'query' method (if available), otherwise use RPC
        # Here, we'll use the 'query' method if available, else fallback to API method
        sql = """
        SELECT AVG(total) AS average_total_last_week
        FROM orders
        WHERE created_at >= NOW() - INTERVAL '7 days';
        """
        try:
            # If your client supports .query (postgrest-py >= 0.10.6)
            response = supabase.query(sql).execute()
            print(f"[DEBUG] Raw SQL response: {response}")
            avg = None
            if response and hasattr(response, 'data') and response.data:
                avg = response.data[0].get('average_total_last_week')
            if avg is not None:
                avg = float(avg)
            print(f"[DEBUG] Average total from SQL: {avg}")
            return avg
        except AttributeError:
            # Fallback: You must create a Postgres function and call it via RPC
            print("[DEBUG] .query method not available. Please create a Postgres function for this aggregate.")
            return None
    except Exception as e:
        logging.error(f"Error fetching average total via SQL: {e}")
        return None

