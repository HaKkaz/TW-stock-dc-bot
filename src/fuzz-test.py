#! /usr/bin/python3
from unittest.mock import AsyncMock
import afl
import sys
import asyncio
import os
from commands import price, ma31, best4Buy, best4Sell


async def test_price(data):
    # 模擬 Discord 的 ctx
    try:
        ctx = AsyncMock()
        ctx.send = AsyncMock()
        await price(ctx, data)
        print("success")

    except Exception:
        # print error
        print("error")
        exit(1)

    return


async def test_best4buy(data):

    # 模擬 Discord 的 ctx
    try:
        ctx = AsyncMock()
        ctx.send = AsyncMock()
        await best4Buy(ctx, data)

    except Exception:
        # print error
        print("error")
        exit(1)


async def test_best4Sell(data):

    # 模擬 Discord 的 ctx
    try:
        ctx = AsyncMock()
        ctx.send = AsyncMock()
        await best4Sell(ctx, data)

    except Exception:
        # print error
        print("error")
        exit(1)


async def test_ma31(data):

    # 模擬 Discord 的 ctx
    try:
        ctx = AsyncMock()
        ctx.send = AsyncMock()
        await ma31(ctx, data, '10')

    except Exception:
        # print error
        print("error")
        exit(1)


if __name__ == "__main__":
    afl.init()
    data = sys.stdin.read()
    asyncio.run(test_price(data))
    asyncio.run(test_best4buy(data))
    asyncio.run(test_best4Sell(data))
    asyncio.run(test_ma31(data))
    os._exit(0)
