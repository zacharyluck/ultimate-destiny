import pydest
import asyncio
from dotenv import load_dotenv
import os


load_dotenv()


# use pydest to pull manifest
async def main():
    destiny = pydest.Pydest(os.getenv('BUNGIE_API'))

    res = await destiny.api._get_request('https://www.bungie.net/Platform/Destiny2/Manifest/')

    print(res)

    await destiny.close()

loop = asyncio.get_event_loop()
df = loop.run_until_complete(main())
loop.close()
