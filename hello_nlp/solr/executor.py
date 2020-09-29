import httpx

async def passthrough(uri):
    async with httpx.AsyncClient() as client:
        r = await client.get(uri)
    return r