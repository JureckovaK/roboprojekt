"""
Client which send messages to server
"""
import asyncio
import aiohttp
import pyglet

from interface_frontend import draw_interface, create_window, handle_text
from interface import InterfaceState
from backend import State


class Interface:
    def __init__(self):
        self.window = create_window()
        self.window.push_handlers(
            on_draw=self.window_draw,
            on_text=self.on_text, )
        self.state = InterfaceState()
        self.ws = None

    def window_draw(self):
        self.window.clear()
        draw_interface(self.state, self.window)

    def on_text(self, text):
        """
        Key listener.
        Wait for user input on keyboard and react for it.
        """
        handle_text(self.state, text)
        self.send_to_server(self.state.as_dict())

    def send_to_server(self, message):
        """
        Client sends messages to server.
        """
        print(message)
        if self.ws:
            asyncio.ensure_future(self.ws.send_json(message))

    async def get_messages(self):
        """
        Client connects to server and receives messages.
        """
        # create Session
        async with aiohttp.ClientSession() as session:
            # create Websocket
            async with session.ws_connect('http://localhost:8080/interface/') as self.ws:
                async for msg in self.ws:
                    # Cycle "for" is finished when client disconnect from server
                    message = msg.json()
                    if "robot_name" in message:
                        robot_name = message["robot_name"]
                    if "game_state" in message:
                        self.set_game_state(message, robot_name)
                    if "cards" in message:
                        self.set_dealt_cards(message)
                    else:
                        print(message)
        self.ws = None

    def set_game_state(self, message, robot_name):
        self.game_state = State.from_dict(message)
        self.state.players = self.game_state.robots
        for robot in self.state.players:
            if robot.name == robot_name:
                self.state.robot = robot
                index = self.state.players.index(robot)
                del self.state.players[index]

    def set_dealt_cards(self, message):
        self.state.dealt_cards = self.game_state.cards_from_dict(message)
        # Set the game round for this client - it is changed only
        # by message from server
        self.state.my_game_round = message["current_game_round"]


def tick_asyncio(dt):
    """
    Schedule an event loop.
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(0))


def main():
    interface = Interface()

    pyglet.clock.schedule_interval(tick_asyncio, 1/30)
    asyncio.ensure_future(interface.get_messages())


if __name__ == "__main__":
    main()
    pyglet.app.run()
