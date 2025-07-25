"""Rate limiting utility for chat messages."""
import time
from .redis_pool import get_redis_connection
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter using Redis."""
    
    def __init__(self, max_messages=30, window_seconds=60):
        self.max_messages = max_messages
        self.window_seconds = window_seconds
        self.redis = get_redis_connection()
    
    def is_allowed(self, user_id):
        """Check if user is allowed to send a message."""
        try:
            key = f"rate_limit:user:{user_id}"
            current_time = int(time.time())
            window_start = current_time - self.window_seconds
            
            # Remove old entries
            self.redis.zremrangebyscore(key, 0, window_start)
            
            # Count messages in current window
            message_count = self.redis.zcard(key)
            
            if message_count >= self.max_messages:
                return False
            
            # Add current message
            self.redis.zadd(key, {str(current_time): current_time})
            self.redis.expire(key, self.window_seconds)
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            # Allow message on error to not block users
            return True


def validate_message(content):
    """Validate message content."""
    if not content:
        return False, "Message cannot be empty"
    
    # Strip whitespace
    content = content.strip()
    
    if not content:
        return False, "Message cannot be empty"
    
    if len(content) > 1000:
        return False, "Message too long (max 1000 characters)"
    
    # Check for excessive newlines
    if content.count('\n') > 10:
        return False, "Too many line breaks"
    
    return True, content