"""
The frontend module
    - deal with graphic output
    - define a Pyglet window for drawing and create sprites from images
"""

import pyglet
from pathlib import Path

# Constatnts for size of tile image in px
TILE_WIDTH = 64
TILE_HEIGHT = 64

# Loading of tiles and robots images
loaded_tiles_images = {}
for image_path in Path('./img/tiles/png').iterdir():
    loaded_tiles_images[image_path.stem] = pyglet.image.load(image_path)

loaded_robots_images = {}
for image_path in Path('./img/robots_map/png').iterdir():
    loaded_robots_images[image_path.stem] = pyglet.image.load(image_path)


def create_window(state):
    """
    Return a pyglet window for graphic output.

    state: State object containing game board, robots and map sizes
    """
    window = pyglet.window.Window(state.tile_count[0] * TILE_WIDTH,
                                  state.tile_count[1] * TILE_HEIGHT, resizable=True)
    return window


def load_tiles(state):
    """
    Return list of sprites of tiles.

    state: State object containing game board and robots
    """
    tile_sprites = []
    for coordinate, tiles in state._board.items():
        sprites = create_tile_sprites(coordinate, tiles)
        tile_sprites.extend(sprites)
    return tile_sprites


def load_robots(state):
    """
    Return list of sprites of robots.

    state: State object containing game board and robots
    """
    robot_sprites = []
    named_robot_sprites = {}
    # Only active robots will be drawn.
    for robot in state.get_active_robots():
        robot_sprite = create_robot_sprite(robot)
        named_robot_sprites[robot.name] = robot_sprite
        robot_sprites.append(robot_sprite)
    return robot_sprites, named_robot_sprites


def create_tile_sprites(coordinate, tiles):
    """
     Return list of sprites of tiles.

    coordinate: coordinate of tiles
    tiles = list of Tile
    """
    tile_sprites = []
    for tile in tiles:
        rotation = tile.direction.value
        x, y = coordinate
        img = loaded_tiles_images[tile.name]
        img.anchor_x = img.width//2
        img.anchor_y = img.height//2
        tile_x = x*TILE_WIDTH
        tile_y = y*TILE_HEIGHT
        tile_sprite = pyglet.sprite.Sprite(img, x=img.anchor_x + tile_x,
                                                y=img.anchor_y + tile_y)
        tile_sprite.rotation = rotation
        tile_sprites.append(tile_sprite)
    return tile_sprites


def create_robot_sprite(robot):
    """
    Return sprite of robot.
    """
    rotation = robot.direction.value
    x, y = robot.coordinates
    img = loaded_robots_images[robot.name]
    img.anchor_x = img.width//2
    img.anchor_y = img.height//2
    robot_x = x*TILE_WIDTH
    robot_y = y*TILE_HEIGHT
    robot_sprite = pyglet.sprite.Sprite(img, x=img.anchor_x + robot_x,
                                             y=img.anchor_y + robot_y)
    robot_sprite.rotation = rotation
    return robot_sprite


def draw_state(state, window, game_log=[]):
    """
    Draw the images of tiles and robots into map, react to user's resizing of window by scaling the board.

    state: State object containing game board, robots and map sizes
    """
    tile_sprites = load_tiles(state)
    if not game_log:
        robot_sprites, named_robot_sprites = load_robots(state)
        tile_sprites.extend(robot_sprites)

    # Scaling
    pyglet.gl.glPushMatrix()

    # Scaling ratio
    zoom = min(
        window.height / (state.tile_count[1] * TILE_HEIGHT),
        window.width / (state.tile_count[0] * TILE_WIDTH)
    )

    pyglet.gl.glScalef(zoom, zoom, 1)

    for tile_sprite in tile_sprites:
        tile_sprite.draw()
    if game_log:
        draw_robots(state, game_log)

    pyglet.gl.glPopMatrix()


def draw_robots(state, game_log):
    robot_sprites, named_robot_sprites = load_robots(state)
    if game_log["cards"]:
        for card in game_log["cards"]:
            if "MovementCard" in card:
                moves = card["MovementCard"]
                for move in moves:
                    for robot_name, coor_delta in move.items():
                        robot_sprite = named_robot_sprites[robot_name]
                        x, y = tuple(coor_delta)
                        step_x = x/100
                        step_y = y/100
                        for _ in range(1, 100):
                            robot_sprite.x = robot_sprite.x + step_x
                            robot_sprite.y = robot_sprite.y + step_y
                            robot_sprite.draw()
