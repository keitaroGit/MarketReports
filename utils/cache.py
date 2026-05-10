"""
Caching utility for data persistence
"""
import os
import json
from datetime import datetime, timedelta
import hashlib

class CacheManager:
    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def get_cache_path(self, key):
        """Generate cache file path from key"""
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f'{hash_key}.json')
    
    def get(self, key, ttl_seconds=3600):
        """
        Retrieve cached data if valid
        
        Args:
            key: Cache key
            ttl_seconds: Time to live in seconds
        
        Returns:
            Cached data or None
        """
        cache_path = self.get_cache_path(key)
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                # Check if cache is still valid
                cached_time = datetime.fromisoformat(cache_data.get('timestamp', ''))
                if datetime.now() - cached_time < timedelta(seconds=ttl_seconds):
                    return cache_data.get('data')
            except Exception as e:
                print(f"Error reading cache: {str(e)}")
        
        return None
    
    def set(self, key, data):
        """
        Store data in cache
        
        Args:
            key: Cache key
            data: Data to cache
        """
        cache_path = self.get_cache_path(key)
        
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"Error writing cache: {str(e)}")
    
    def clear(self):
        """Clear all cache"""
        try:
            for file in os.listdir(self.cache_dir):
                os.remove(os.path.join(self.cache_dir, file))
        except Exception as e:
            print(f"Error clearing cache: {str(e)}")
    
    def remove(self, key):
        """Remove specific cache entry"""
        cache_path = self.get_cache_path(key)
        try:
            if os.path.exists(cache_path):
                os.remove(cache_path)
        except Exception as e:
            print(f"Error removing cache: {str(e)}")
