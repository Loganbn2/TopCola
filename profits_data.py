from flask import render_template
import logging
import json  # Import json for serialization
from datetime import datetime, timedelta

def get_order_data(supabase):
    """
    Fetch all order data from the 'orders' table in Supabase.
    Returns a tuple: (orders, error)
    """
    try:
        response = supabase.table('orders').select('*').execute()
        if response.data:
            return response.data, None
        else:
            return [], response.error or 'No data returned from Supabase.'
    except Exception as e:
        logging.error(f"Error fetching order data: {e}")
        return [], str(e)



