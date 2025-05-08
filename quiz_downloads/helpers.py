from django.conf import settings
from django.core.cache import cache
from .supabase_client import get_supabase_client

def upload_file_to_supabase(file, file_path):
    # Get file size efficiently
    file_size = file.size

    # Get current Supabase index atomically
    supabase_index = cache.get_or_set('supabase_index', 0, timeout=None)
    
    # Get storage usage for current bucket atomically
    storage_key = 'storage_usage'
    storage_usage = cache.get_or_set(storage_key, 0, timeout=None)

    # Check if current bucket would exceed 1GB
    if storage_usage + file_size >= 1024 * 1024 * 1024:
        supabase_index = cache.incr('supabase_index')
        if supabase_index >= len(settings.SUPABASE_STORAGES):
            cache.set('supabase_index', len(settings.SUPABASE_STORAGES), timeout=None)  # Reset index
            raise Exception("All Supabase storage buckets are full")
        storage_usage = cache.get_or_set(storage_key, 0, timeout=None)

    # Get Supabase client for current index
    supabase = get_supabase_client(supabase_index)
    if not supabase:
        raise Exception("Supabase storages limits exceeded, no more buckets available")

    bucket_name = settings.SUPABASE_MEDIA_BUCKET
    
    try:
        # Upload file directly without reading into memory
        supabase.storage.from_(bucket_name).upload(file_path, file.read())
        # Update storage usage atomically
        cache.incr(storage_key, file_size)
        return supabase_index
    except Exception as e:
        raise e

# def get_cached_signed_url_from_supabase_storage(path: str, expires_in: int = 60 * 60):
#     bucket_name = settings.SUPABASE_MEDIA_BUCKET
#     cache_key = f"supabase_signed_url:{bucket_name}:{path}"
#     signed_url = cache.get(cache_key)
#     if signed_url:
#         return signed_url

#     response = supabase.storage.from_(bucket_name).create_signed_url(path, expires_in)
#     signed_url = response.get("signedURL")
#     cache.set(cache_key, signed_url, timeout=expires_in - 10)  # buffer for safety
#     return signed_url