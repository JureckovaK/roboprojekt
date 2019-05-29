"""
Client which send one message to server
"""
import asyncio
import sys
import aiohttp
import json
import pyglet

from interface_frontend import draw_interface, create_window, handle_text
from interface import get_interface_state


state = get_interface_state()
window = create_window()

ws = None

@window.event
def on_draw():
    window.clear()
    draw_interface(state, window)


@window.event
def on_text(text):
    handle_text(state, text)
    send_to_server(state)


def send_to_server(state):
    msg = json.dumps(state.my_program)
    print(msg)
    if ws:
        asyncio.ensure_future(ws.send_str(msg))

async def send_one():
    global ws
    # create Session
    async with aiohttp.ClientSession() as session:
        #create Websocket
        async with session.ws_connect('http://localhost:8080/ws/') as ws:
            async for msg in ws:
                # Cycle "for" is finished when client disconnect from server
                if msg.type == aiohttp.WSMsgType.TEXT:
                    message = msg.data
                    print(message)
        ws = None


def tick_asyncio(dt):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(0))

pyglet.clock.schedule_interval(tick_asyncio, 1/30)
asyncio.ensure_future(send_one())

pyglet.app.run()
