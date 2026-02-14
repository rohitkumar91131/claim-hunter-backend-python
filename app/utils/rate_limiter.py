from fastapi import Request, HTTPException, status
from app.config import settings
import time
from collections import defaultdict
import threading

# Simple in-memory storage: IP -> List of timestamps
# Using a lock for basic thread safety
_request_history = defaultdict(list)
_lock = threading.Lock()

RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 5

async def rate_limit_dependency(request: Request):
    """
    Rate limiting dependency for anonymous users.
    Limits requests based on IP address.
    """
    if not settings.ENABLE_RATE_LIMIT:
        return

    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()

    with _lock:
        # Clean up old requests
        _request_history[client_ip] = [
            t for t in _request_history[client_ip]
            if current_time - t < RATE_LIMIT_WINDOW
        ]

        # Check limit
        if len(_request_history[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
            )

        # Record new request
        _request_history[client_ip].append(current_time)
