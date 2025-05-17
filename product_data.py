from flask import render_template
import logging
import json  # Import json for serialization



def get_product_info(supabase, product_id):
    try:
        logging.info(f"Fetching data for product ID {product_id} from the 'products' table...")
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
    
def get_flower_info(supabase, product_id):
    try:
        logging.info(f"Fetching data for product ID {product_id} from the 'weighted_products' table...")
        response = supabase.table('weighted_products').select('*').eq('id', product_id).execute()
        logging.info(f"Supabase response: {response}")
        
        if response.data:
            product_info = response.data[0]  # assuming only one row is returned
            logging.info(f"Product info fetched: {product_info}")

            # Fetch corresponding volume_discounts row
            price_tier = product_info.get('price_tier')
            if price_tier is not None:
                logging.info(f"Fetching data from 'volume_discounts' table for price_tier {price_tier}...")
                discount_response = supabase.table('volume_discounts').select('*').eq('tier', price_tier).execute()
                logging.info(f"Volume discounts response: {discount_response}")

                if discount_response.data:
                    product_info['volume_discounts'] = discount_response.data[0]  # assuming only one row is returned
                    logging.info(f"Volume discounts data added: {product_info['volume_discounts']}")
                else:
                    logging.warning(f"No volume discounts found for price_tier {price_tier}.")
                    product_info['volume_discounts'] = None
            else:
                logging.warning("No price_tier found in product info.")

            return product_info, None
        else:
            logging.warning(f"No product found with ID {product_id}.")
            return None, "Product not found"
    except Exception as e:
        logging.error(f"Error fetching product info for ID {product_id}: {e}")
        return None, f"An error occurred: {str(e)}"


def get_product_ids_by_tag(supabase, tag):
    try:
        logging.info(f"Fetching product IDs with '{tag}' in tags from the 'Products' table...")
        response = supabase.table('products').select('id').filter('tags', 'cs', f'["{tag}"]').execute()
        logging.info(f"Supabase response: {response}")
        
        if response.data:
            product_ids = [item['id'] for item in response.data]
            logging.info(f"Product IDs fetched: {product_ids}")
            return product_ids, None
        else:
            logging.warning(f"No products found with '{tag}' in tags.")
            return [], "No products found"
    except Exception as e:
        logging.error(f"Error fetching product IDs with '{tag}' in tags: {e}")
        return None, f"An error occurred: {str(e)}"

def get_volume_discounts(supabase):
    try:
        logging.info("Fetching all data from the 'volume_discounts' table...")
        response = supabase.table('volume_discounts').select('tier, 4g_discount, 7g_discount, 14g_discount, 28g_discount').execute()
        logging.info(f"Supabase response: {response}")
        
        if response.data:
            volume_discounts = [
                {
                    "tier": item.get("tier"),
                    "4g_discount": item.get("4g_discount"),
                    "7g_discount": item.get("7g_discount"),
                    "14g_discount": item.get("14g_discount"),
                    "28g_discount": item.get("28g_discount")
                }
                for item in response.data
            ]
            logging.info(f"Volume discounts data fetched: {volume_discounts}")
            return volume_discounts, None
        else:
            logging.warning("No data found in the 'volume_discounts' table.")
            return [], "No data found"
    except Exception as e:
        logging.error(f"Error fetching data from the 'volume_discounts' table: {e}")
        return None, f"An error occurred: {str(e)}"
