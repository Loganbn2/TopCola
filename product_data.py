from flask import render_template
import logging

def get_product_list(supabase):
    try:
        logging.info("Fetching data from the 'Products' table...")
        response = supabase.table('products').select('"product_name"').execute()
        logging.info(f"Supabase response: {response}")
        
        if response.data:
            products = [item['product_name'] for item in response.data]
            logging.info(f"Products fetched: {products}")
            return products, None
        else:
            logging.warning("No products found in the 'Products' table.")
            return [], "No products found"
    except Exception as e:
        logging.error(f"Error fetching products: {e}")
        return [], f"An error occurred: {str(e)}"

def get_product_info(supabase, product_id):
    try:
        logging.info(f"Fetching data for product ID {product_id} from the 'Products' table...")
        response = supabase.table('products').select('*').eq('id', product_id).execute()
        logging.info(f"Supabase response: {response}")
        
        if response.data:
            product_info = response.data[0]  # Assuming only one row is returned
            logging.info(f"Product info fetched: {product_info}")
            return product_info, None
        else:
            logging.warning(f"No product found with ID {product_id}.")
            return None, "Product not found"
    except Exception as e:
        logging.error(f"Error fetching product info for ID {product_id}: {e}")
        return None, f"An error occurred: {str(e)}"
