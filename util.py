"""
Util contains classes Tile and Direction, accessed by both loading and backend.
"""

from enum import Enum


class Direction(Enum):
    N = 0, (0, +1), 0
    E = 90, (+1, 0), 1
    S = 180, (0, -1), 2
    W = 270, (-1, 0), 3

    def __new__(cls, degrees, coor_delta, tile_property):
        """
        Get attributes value and vector of the given Direction class values.

        Override standard enum __new__ method.
        vector: new coordinates (where the robot goes to)
        tile_property: map tile property: value (custom - added in Tiled).
        Makes it possible to change vector and tile_property when the object is rotated.
        With degrees change (value) there comes the coordinates (vector) change and tile_property.

        More info about enum - official documentation: https://docs.python.org/3/library/enum.html
        Blog post with the exact __new__() usage: http://xion.io/post/code/python-enums-are-ok.html
        """
        obj = object.__new__(cls)
        obj._value_ = degrees
        obj.coor_delta = coor_delta
        obj.map_property = tile_property
        return obj

    def __add__(self, other):
        return Direction((self.value + other.value) % 360)

    def get_new_direction(self, where_to):
        """
        Get new direction of given object.
        Change attribute direction according to argument where_to, passed from class Rotation.
        """
        return Direction(self + where_to)


class Rotation(Enum):
    """
    Class describing the direction of the movement of the object-robot (dynamic).
    """
    LEFT = -90
    RIGHT = 90
    U_TURN = 180


class Tile:
    def __init__(self, direction, path, properties):
        self.direction = direction
        self.path = path

    def __repr__(self):
        # type(self).__name__: shows the type of the particular tile
        # eg. HoleTile, WallTile or just Tile
        return "<{} {}>".format(type(self).__name__, self.direction)

    def can_move_from(self, direction):
        """
        Verify movement from tile in specific direction.

        Return a boolean.

        True - There is not a wall in direction of the move.
        False - There is a wall in direction of the move.
        """
        return True

    def can_move_to(self, direction):
        """
        Verify movement to tile from specific direction.

        Return a boolean.

        True - There is not a wall in direction of the move.
        False - There is a wall in direction of the move.
        """
        return True

    def kill_robot(self, robot):
        """
        Take away one robot life, set him to inactive mode and move him
        to coordinates for inactive robots (-1, -1).

        Take and return Robot class.
        """
        return robot

    def push_robot(self, robot, state):
        """
        Move robot by one tile in specific game round.

        robot: Robot class
        state: State class containing game round

        Return Robot class.
        """
        return robot

    def rotate_robot(self, robot):
        """
        Rotate robot by 90° to the left or right according to tile properties.

        Take and return Robot class.
        """
        return robot

    def shoot_robot(self, robot, state):
        """
        Shoot robot with tile laser.

        robot: Robot class
        state: State class

        Return Robot class.
        """
        return robot

    def collect_flag(self, robot):
        """
        Collect flag by robot and change robot's start coordinates.

        Take and return Robot class.
        """
        return robot

    def repair_robot(self, robot, state):
        """
        Repair one robot's damage. Change robot's start coordinates, if possible by tile properties.

        robot: Robot class
        state: State class

        Return Robot class.
        """
        return robot


class WallTile(Tile):
    def can_move_from(self, direction):
        # The direction of the wall is the same as the direction in which
        # robot wants to move from the tile.
        return not (self.direction == direction)

    def can_move_to(self, direction):
        # If there is a wall in direction of the robot movement,
        # then the direction of the robot goes against the direction of the wall.
        # Because of that the tile is checked in upside down direction.
        return not (self.direction.get_new_direction(Rotation.U_TURN) == direction)


class StartTile(Tile):
    # Start tile has no tile effect.
    pass


class HoleTile(Tile):
    def __init__(self, direction=Direction.N, path=None, properties=[]):
        super().__init__(direction, path, properties)

    def kill_robot(self, robot):
        # Call robot's method for dying.
        return robot.die()


class BeltTile(Tile):
    def __init__(self, direction, path, properties):
        self.belt_rotation = self.transform_direction(properties[0]["value"])
        self.express = properties[1]["value"]
        super().__init__(direction, path, properties)

    def transform_direction(self, direction_integer):
        """
        Method to transform the integer taken from json properties
         to valid Direction class instance for later processing.
        """
        if direction_integer == 0:
            return Direction.N
        if direction_integer == 90:
            return Rotation.RIGHT
        if direction_integer == -90:
            return Rotation.LEFT
        if direction_integer == 180:
            return Rotation.U_TURN


class PusherTile(Tile):
    def __init__(self, direction, path, properties):
        self.game_round = properties[0]["value"]
        super().__init__(direction, path, properties)

    def push_robot(self, robot, state):
        # Check game round and activate correct pushers.
        # PusherTile property game_round:
        #  0 for even game round number,
        #  1 for odd game round number.
        if state.game_round % 2 == self.game_round:
            robot.move(self.direction.get_new_direction(Rotation.U_TURN), 1, state)


class GearTile(Tile):
    def __init__(self, direction, path, properties):
        self.move_direction = self.transform_direction(properties[0]["value"])
        super().__init__(direction, path, properties)

    def transform_direction(self, direction_string):
        """
        Method to transform the string taken from json properties to valid Rotation class instance for later processing.
        """
        if direction_string == "left":
            return Rotation.LEFT
        if direction_string == "right":
            return Rotation.RIGHT

    def rotate_robot(self, robot):
        # Rotate robot by 90° according to GearTile property: left or right.
        robot.rotate(self.move_direction)


class LaserTile(Tile):
    def __init__(self, direction, path, properties):
        self.laser_strength = properties[0]["value"]
        self.laser_start = properties[1]["value"]
        super().__init__(direction, path, properties)

    def shoot_robot(self, robot, state):
        # Robot stands on laser tile.
        hit = True
        # If robot isn't standing on the start of the laser, look for other robots.
        if not self.laser_start:
            # Get coordinates of current robot.
            (x, y) = robot.coordinates
            # Get coordinates of other robots.
            coordinates = []
            for robot_state in state.robots:
                coordinates.append(robot_state.coordinates)
            # Get direction in which it will be checked for other robots or laser start.
            direction_to_start = self.direction.get_new_direction(Rotation.U_TURN)
            # Check if there is another robot in direction of incoming laser.
            while hit:
                # Get new coordinates.
                (x, y) = get_next_coordinates((x, y), direction_to_start)
                # Check for other robots.
                if (x, y) in coordinates:
                    # There is another robot.
                    # Current robot won't be hit by laser.
                    hit = False
                    break
                # Get new tiles.
                new_tiles = state.get_tiles((x, y))
                for tile in new_tiles:
                    # Check if new tiles contain follow-up LaserTile in correct direction.
                    if isinstance(tile, LaserTile) and tile.direction == self.direction:
                        # Follow-up laser tile found, don't check ohter tiles here.
                        break
                # Check for laser start tile.
                if isinstance(tile, LaserTile) and tile.laser_start:
                    # Don't check new tiles.
                    break
        if hit:
            # No robots found in the direction of incoming laser.
            # So do damage to robot.
            if robot.damages < (10 - self.laser_strength):
                # Laser won't kill robot, but it will damage robot.
                robot.damages += self.laser_strength
            else:
                # Robot is damaged so much that laser kills him.
                robot.die()


class FlagTile(Tile):
    def __init__(self, direction, path, properties):
        self.flag_number = properties[0]["value"]
        super().__init__(direction, path, properties)

    def collect_flag(self, robot):
        # Robot always change his starting coordinates, when he is on a flag.
        # Flag number doesn't play a role.
        robot.start_coordinates = robot.coordinates
        # Collect only correct flag.
        # Correct flag will have a number that is equal to robot's flag number plus one.
        if (robot.flags + 1) == self.flag_number:
            robot.flags += 1


class RepairTile(Tile):
    def __init__(self, direction, path, properties):
        self.new_start = properties[0]["value"]
        super().__init__(direction, path, properties)

    def repair_robot(self, robot, state):
        if state.game_round == 5:
            # Remove one robot damage.
            if robot.damages > 0:
                robot.damages -= 1
        # Change starting coordinates of robot, if it's a tile property.
        if self.new_start:
            robot.start_coordinates = robot.coordinates


TILE_CLS = {'wall': WallTile, 'starting_square': StartTile, 'hole': HoleTile,
            'laser': LaserTile, 'gear': GearTile, 'pusher': PusherTile,
            'belt': BeltTile, 'flag': FlagTile, 'repair': RepairTile,
            'ground': Tile}


def select_tile(direction, path, type, properties):
    """
    Select tile subclass according to its type and create coressponding subclass.
    """
    return TILE_CLS[type](direction, path, properties)


def get_next_coordinates(coordinates, direction):
    """
    Get next coordinates in the given direction from current coordinates.
    """
    (x, y) = coordinates
    (new_x, new_y) = direction.coor_delta
    x = x + new_x
    y = y + new_y
    return (x, y)
