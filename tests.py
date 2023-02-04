import asyncio
from collections import AsyncIterable


async def er(repeat):
    gen = ["r", "b", "c", "m", "k"]
    rg = [5, 4, 3, 2, 1]
    async for i, k in AsyncIterable(gen):
        async for j in AsyncIterable(gen):
            await asyncio.sleep(k)
            print(i, j, k)

er(1)
