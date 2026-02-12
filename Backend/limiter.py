"""
Rate limiter configuration using SlowAPI.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Create a limiter instance that uses the client's IP address
limiter = Limiter(key_func=get_remote_address)
