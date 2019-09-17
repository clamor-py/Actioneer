import asyncio
import actioneer


handler = actioneer.Performer(loop=asyncio.get_event_loop())


@handler.register
@actioneer.Action
async def ping(arg1):
    print("pong!", arg1)


handler.run("ping hello")
