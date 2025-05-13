from flask import render_template
import logging
import json  # Import json for serialization



def get_product_info(supabase, product_id):
    try:
        logging.info(f"Fetching data for product ID {product_id} from the 'Products' table...")
        response = supabase.table('products').select('*').eq('id', product_id).execute()
        logging.info(f"Supabase response: {response}")
        
        if response.data:
            product_info = response.data[0]  # assuming only one row is returned
            logging.info(f"Product info fetched: {product_info}")
            return product_info, None
        else:
            logging.warning(f"No product found with ID {product_id}.")
            return None, "Product not found"
    except Exception as e:
        logging.error(f"Error fetching product info for ID {product_id}: {e}")
        return None, f"An error occurred: {str(e)}"


def get_sativa_product_ids(supabase):
    try:
        logging.info("Fetching product IDs with 'sativa' in tags from the 'Products' table...")
        response = supabase.table('products').select('id').filter('tags', 'cs', '["sativa"]').execute()
        logging.info(f"Supabase response: {response}")
        
        if response.data:
            product_ids = [item['id'] for item in response.data]
            logging.info(f"Product IDs fetched: {product_ids}")
            return product_ids, None
        else:
            logging.warning("No products found with 'sativa' in tags.")
            return [], "No products found"
    except Exception as e:
        logging.error(f"Error fetching product IDs with 'sativa' in tags: {e}")
        return None, f"An error occurred: {str(e)}"
