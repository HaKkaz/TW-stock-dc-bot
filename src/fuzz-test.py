import afl
import sys
import asyncio
import pytest
from hypothesis import given
from hypothesis.strategies import text
from commands import price, ma31

@pytest.mark.asyncio
@given(text())
async def test_fuzz(data):
    try:
        # Call your function with the fuzzed input
        await price(data)
        await ma31(data, '10')
    except Exception:
        pass

if __name__ == "__main__":
    asyncio.run(test_fuzz())
