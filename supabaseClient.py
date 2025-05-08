from supabase import create_client

SUPABASE_URL = "https://your-supabase-url.supabase.co"  # Replace with your Supabase URL
SUPABASE_ANON_KEY = "your-anon-key"  # Replace with your Supabase anon key

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
