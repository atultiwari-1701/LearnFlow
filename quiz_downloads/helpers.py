from .supabase_client import supabase
from django.conf import settings
from django.core.cache import cache

def upload_file_to_supabase(file, file_path):
    bucket_name = settings.SUPABASE_MEDIA_BUCKET
    content = file.read()
    file.seek(0)
    supabase.storage.from_(bucket_name).upload(file_path, content)

def get_cached_signed_url(path: str, expires_in: int = 60 * 60):
    bucket_name = settings.SUPABASE_MEDIA_BUCKET
    cache_key = f"supabase_signed_url:{bucket_name}:{path}"
    signed_url = cache.get(cache_key)
    if signed_url:
        return signed_url

    response = supabase.storage.from_(bucket_name).create_signed_url(path, expires_in)
    signed_url = response.get("signedURL")
    cache.set(cache_key, signed_url, timeout=expires_in - 10)  # buffer for safety
    return signed_url