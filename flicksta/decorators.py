from functools import wraps
from django.conf import settings
from django.http import JsonResponse
from django.core.cache import cache
import time

def rate_limit(
    per_minute=None,
    per_hour=None, 
    per_day=None,
    cache_prefix="rate_limit",
    error_message="Rate limit exceeded",
    require_auth=True
):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Handle authentication requirement
            if require_auth:
                if not request.user.is_authenticated:
                    return JsonResponse({'error': 'Authentication required'}, status=401)
                user_id = request.user.id
            else:
                # Use IP address for anonymous users
                user_id = request.META.get('REMOTE_ADDR', 'anonymous')
            
            current_time = int(time.time())
            
            # Check each time window if limit is specified
            limits_to_check = []
            if per_minute:
                limits_to_check.append(('minute', per_minute, 60, current_time // 60))
            if per_hour:
                limits_to_check.append(('hour', per_hour, 3600, current_time // 3600))
            if per_day:
                limits_to_check.append(('day', per_day, 86400, current_time // 86400))
            
            for window_name, limit, window_seconds, window_id in limits_to_check:
                cache_key = f"{cache_prefix}_{user_id}_{window_name}_{window_id}"
                
                try:
                    # Using atomic increment - preventing race conditions
                    current_count = cache.get(cache_key, 0)
                    if current_count >= limit:
                        return JsonResponse({
                            'error': f'{error_message}. Too many requests per {window_name}.',
                            'limit': limit,
                            'window': window_name,
                            'current_count': current_count,
                            'reset_time': (window_id + 1) * window_seconds
                        }, status=429)
                    
                    # Increment counter atomically
                    new_count = cache.get_or_set(cache_key, 0, window_seconds)
                    if new_count == 0:
                        # First request in this window
                        cache.set(cache_key, 1, window_seconds)
                    else:
                        # Use Redis INCR for atomic increment if using Redis
                        try:
                            from django_redis import get_redis_connection
                            redis_conn = get_redis_connection("default")
                            new_count = redis_conn.incr(cache_key)
                            redis_conn.expire(cache_key, window_seconds)
                            
                            if new_count > limit:
                                return JsonResponse({
                                    'error': f'{error_message}. Too many requests per {window_name}.',
                                    'limit': limit,
                                    'window': window_name,
                                    'current_count': new_count,
                                    'reset_time': (window_id + 1) * window_seconds
                                }, status=429)
                        except ImportError:
                            # Fallback for non-Redis backends
                            cache.set(cache_key, current_count + 1, window_seconds)
                            
                except Exception as e:
                    print(f"Rate limit cache error: {e}")
            
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator
# Convenience functions for common use cases
def upload_rate_limit():
    limits = settings.UPLOAD_RATE_LIMIT
    return rate_limit(
        per_minute=limits['per_minute'],
        per_hour=limits['per_hour'],
        per_day=limits['per_day'],
        cache_prefix="upload_rate",
        error_message="Upload rate limit exceeded"
    )

def create_post_rate_limit():
    limits = settings.CREATE_POST_RATE_LIMIT
    return rate_limit(
        per_minute=limits['per_minute'],
        per_hour=limits['per_hour'],
        per_day=limits['per_day'],
        cache_prefix="create_post_rate",
        error_message="Post Creation rate limit exceeded"
    )

def email_rate_limit():
    limits = settings.EMAIL_RATE_LIMIT
    return rate_limit(
        per_minute=limits['per_minute'],
        per_hour=limits['per_hour'],
        per_day=limits['per_day'],
        cache_prefix="email_rate",
        error_message="Email rate limit exceeded"
    )