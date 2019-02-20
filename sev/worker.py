import aiohttp
import asyncio
import json

QUEUE = asyncio.Queue()


async def consume():
    msg = await QUEUE.get()
    session = aiohttp.ClientSession()
    async with session.ws_connect('wss://pubsub-edge.twitch.tv') as ws:
        await ws.send_json({
            "type": "LISTEN",
            "data": {
                "topics": [f"channel-bits-events-v1.{msg['usr_id']}"],
                "auth_token": msg['auth_token']
            }
        })

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                pass
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                break


def main():
    data = json.loads(open('/tmp/data.json').read())
    asyncio.run(QUEUE.put(data))
    asyncio.run(consume())
