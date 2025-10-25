from supabase import create_client

from app.settings import settings

supabase_client = create_client(settings.supabase_url, settings.supabase_service_key)
