import pytest
from app.rate_limit.token_bucket import TokenBucketLimiter
from app.core.exceptions import RateLimitError
@pytest.mark.asyncio
async def test_rate_limit():
    x=TokenBucketLimiter(1,0); await x.consume("u")
    with pytest.raises(RateLimitError): await x.consume("u")
