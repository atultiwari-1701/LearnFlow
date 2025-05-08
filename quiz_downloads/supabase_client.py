from supabase import create_client
from django.conf import settings
from django.core.cache import cache

SUPABASE_STORAGES = settings.SUPABASE_STORAGES

def get_supabase_client(index: int):
    if index >= len(SUPABASE_STORAGES):
        return None
    return create_client(SUPABASE_STORAGES[index]['SUPABASE_URL'], SUPABASE_STORAGES[index]['SUPABASE_KEY'])