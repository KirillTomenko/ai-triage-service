import time
from collections import defaultdict
from fastapi import HTTPException

# Simple sliding-window: track request timestamps per client_id
_request_log: dict[str, list[float]] = defaultdict(list)

RATE_LIMIT_REQUESTS = 10   # max requests
RATE_LIMIT_WINDOW = 60     # per N seconds


def check_rate_limit(client_id: str) -> None:
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW

    timestamps = _request_log[client_id]
    # drop old entries
    _request_log[client_id] = [t for t in timestamps if t > window_start]

    if len(_request_log[client_id]) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: max {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW}s for this client.",
        )

    _request_log[client_id].append(now)
