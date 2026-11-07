import asyncio, time
from dataclasses import dataclass
from app.core.exceptions import RateLimitError
@dataclass
class Bucket: tokens: float; last: float
class TokenBucketLimiter:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity=capacity; self.refill_rate=refill_rate; self._b={}; self._lock=asyncio.Lock()
    async def consume(self,key:str,cost:float=1.0):
        async with self._lock:
            now=time.monotonic(); b=self._b.get(key,Bucket(float(self.capacity),now))
            b.tokens=min(self.capacity,b.tokens+(now-b.last)*self.refill_rate); b.last=now
            if b.tokens < cost:
                self._b[key]=b; raise RateLimitError("Too many requests; please retry shortly")
            b.tokens-=cost; self._b[key]=b
