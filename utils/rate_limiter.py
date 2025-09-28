import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests_per_minute):
        self.max_requests = max_requests_per_minute
        self.requests = defaultdict(list)  # user_id -> list of timestamps

    def is_allowed(self, user_id):
        now = time.time()
        window_start = now - 60
        timestamps = self.requests[user_id]

        # Remove timestamps older than 60 seconds
        while timestamps and timestamps[0] < window_start:
            timestamps.pop(0)

        if len(timestamps) < self.max_requests:
            timestamps.append(now)
            return True
        return False
