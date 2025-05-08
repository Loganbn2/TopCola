from supabaseClient import supabase

def fetch_data(table_name: str):
    response = supabase.table(table_name).select("*").execute()
    if response.error:
        raise Exception(f"Error fetching data: {response.error.message}")
    return response.data
