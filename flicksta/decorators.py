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
            if per_minute:
                minute_key = f"{cache_prefix}_{user_id}_minute_{current_time // 60}"
                minute_count = cache.get(minute_key, 0)
                
                if minute_count >= per_minute:
                    return JsonResponse({
                        'error': f'{error_message}. Too many requests per minute.',
                        'limit': per_minute,
                        'window': 'minute'
                    }, status=429)
                
                cache.set(minute_key, minute_count + 1, 60)
            
            if per_hour:
                hour_key = f"{cache_prefix}_{user_id}_hour_{current_time // 3600}"
                hour_count = cache.get(hour_key, 0)
                
                if hour_count >= per_hour:
                    return JsonResponse({
                        'error': f'{error_message}. Too many requests per hour.',
                        'limit': per_hour,
                        'window': 'hour'
                    }, status=429)
                
                cache.set(hour_key, hour_count + 1, 3600)
            
            if per_day:
                day_key = f"{cache_prefix}_{user_id}_day_{current_time // 86400}"
                day_count = cache.get(day_key, 0)
                
                if day_count >= per_day:
                    return JsonResponse({
                        'error': f'{error_message}. Too many requests per day.',
                        'limit': per_day,
                        'window': 'day'
                    }, status=429)
                
                cache.set(day_key, day_count + 1, 86400)
            
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