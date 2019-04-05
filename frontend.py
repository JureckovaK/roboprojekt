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
    # Only active robots will be drawn.
    for robot in state.get_active_robots():
        robot_sprite = create_robot_sprite(robot)
        robot_sprites.append(robot_sprite)
    return robot_sprites


def create_tile_sprites(coordinate, tiles):
    """
    Return list of sprites of items.

    coordinate: coordinate of tiles
    tiles = list of Tile
    """
    tile_sprites = []
    for tile in tiles:
        rotation = tile.direction.value
        path = tile.path
        x, y = coordinate
        img = pyglet.image.load(path)
        img.anchor_x = img.width//2
        img.anchor_y = img.height//2
        tile_x = x*TILE_WIDTH
        tile_y = y*TILE_HEIGHT
        img_sprite = pyglet.sprite.Sprite(img, x=img.anchor_x + tile_x,
                                               y=img.anchor_y + tile_y)
        img_sprite.rotation = rotation
        tile_sprites.append(img_sprite)
    return tile_sprites


def create_robot_sprite(robot):
    """
    Return sprite of robot.
    """
    rotation = robot.direction.value
    path = Path("./img/robots/png/" + robot.name + ".png")
    x, y = robot.coordinates
    img = pyglet.image.load(path)
    img.anchor_x = img.width//2
    img.anchor_y = img.height//2
    robot_x = x*TILE_WIDTH
    robot_y = y*TILE_HEIGHT
    robot_sprite = pyglet.sprite.Sprite(img, x=img.anchor_x + robot_x,
                                           y=img.anchor_y + robot_y)
    robot_sprite.rotation = rotation
    return robot_sprite


def draw_state(state, window):
    """
    Draw the images of tiles and robots into map, react to user's resizing of window by scaling the board.

    state: State object containing game board, robots and map sizes
    """
    tile_sprites = load_tiles(state)
    robot_sprites = load_robots(state)
    tile_sprites.extend(robot_sprites)

    #scaling
    pyglet.gl.glPushMatrix()

    #scaling ratio
    zoom = min(
        window.height / (state.tile_count[1] * TILE_HEIGHT),
        window.width / (state.tile_count[0] * TILE_WIDTH)
    )

    pyglet.gl.glScalef(zoom, zoom, 1)

    for tile_sprite in tile_sprites:
        tile_sprite.draw()

    pyglet.gl.glPopMatrix()
