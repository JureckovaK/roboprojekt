import pytest

from backend import create_robots, Robot, State, MovementCard
from backend import RotationCard, get_direction_from_coordinates
from backend import get_robot_names
from util import Direction, Rotation
from tile import Tile, PusherTile
from loading import get_board


def test_robots_on_start_coordinates():
    """
    Assert that the result of create_robots is a list which contains
    Robot objects with correct attribute coordinates.
    """
    board = get_board("maps/test_3.json")
    robots = create_robots(board)
    assert isinstance(robots, list)
    assert isinstance(robots[0], Robot)


def test_start_state():
    """
    Assert that created start state (board and robots) contains
    the correct instances of objects.
    """
    ss = State.get_start_state("maps/test_3.json")
    assert isinstance(ss, State)
    assert isinstance(ss.robots, list)
    assert isinstance(ss.robots[0], Robot)
    assert isinstance(ss._board, dict)
    assert isinstance(ss._board[0, 0], list)
    assert isinstance(ss._board[0, 0][0], Tile)


# I'd leave this test as regression test - uses robot.walk() method.
@pytest.mark.parametrize(("input_coordinates", "input_direction", "distance", "output_coordinates"),
                         [((3, 3), Direction.N, 2, (3, 5)),
                          ((3, 3), Direction.E, 2, (3, 3)),
                          ((3, 3), Direction.S, 2, (3, 2)),
                          ((3, 3), Direction.W, 2, (2, 3)),
                          ((5, 1), Direction.E, 2, (7, 1))])
def test_robot_walk(input_coordinates, input_direction, distance, output_coordinates):
    """
    Take robot's coordinates, direction and distance and assert robot walked
    to correct coordinates.
    """
    state = State.get_start_state("maps/test_3.json")
    robot = Robot(input_direction, input_coordinates, "tester")
    robot.walk(distance, state, input_direction)
    assert robot.coordinates == output_coordinates

# I'd leave this test as regression test - uses robot.move() method.
@pytest.mark.parametrize(("input_coordinates", "input_direction", "distance", "output_coordinates"),
                         [((0, 1), Direction.N, 3, (0, 4)),
                          ((8, 1), Direction.N, 3, (8, 3)),
                          ((10, 1), Direction.N, 3, (10, 2)),
                          ((3, 3), Direction.E, 2, (3, 3)),
                          ((3, 3), Direction.S, 2, (3, 2)),
                          ((3, 3), Direction.W, 2, (2, 3)),
                          ((5, 1), Direction.E, 2, (5, 1))])
def test_robot_move(input_coordinates, input_direction, distance, output_coordinates):
    """
    Take robot's coordinates, move's direction and distance and assert robot
    was moved to correct coordinates.
    """
    state = State.get_start_state("maps/test_3.json")
    robot = Robot(Direction.N, input_coordinates, "tester")
    robot.move(input_direction, distance, state)
    assert robot.coordinates == output_coordinates


# I'd leave this test as regression test - uses robot.rotate() method.
@pytest.mark.parametrize(("current_direction", "towards", "new_direction"),
                         [(Direction.N, Rotation.LEFT, Direction.W),
                         (Direction.S, Rotation.RIGHT, Direction.W),
                         (Direction.E, Rotation.U_TURN, Direction.W)])
def test_robot_change_direction(current_direction, towards, new_direction):
    """
    Assert that robot rotates correctly according to given rotation.
    """
    robot = Robot(current_direction, None, "tester")
    robot.rotate(towards)
    assert robot.direction == new_direction


def test_robot_on_start_has_the_correct_direction():
    """
    When robot is created, his direction shoud be the same as the direction
    of start tile he stands on.
    Assert the direction is correcly initiated.
    """
    state = State.get_start_state("maps/test_start_direction.json")
    for robot in state.robots:
        tile_direction = state.get_tiles(robot.coordinates)[0].direction
        assert robot.direction == tile_direction


@pytest.mark.parametrize(("robot_index", "expected_coordinates"),
                         [(0, (0, 0)),
                          (1, (1, 0)),
                          (2, (2, 0)),
                          (3, (3, 0)),
                          ])
def test_robots_order_on_start(robot_index, expected_coordinates):
    """
    The order of robots list should reflect their starting positions.
    First robot from the list stands on first start tile and so on.
    Assert the list is correcly created.
    Test to check the behaviour in Python 3.5.
    """
    state = State.get_start_state("maps/test_start_direction.json")
    current_robot = state.robots[robot_index]
    assert current_robot.coordinates == expected_coordinates


@pytest.mark.parametrize(("start_coordinates", "stop_coordinates", "output_direction"),
                         [((0, 0), (0, 1), Direction.N),
                         ((0, 1), (0, 0), Direction.S),
                         ((0, 0), (1, 0), Direction.E),
                         ((1, 0), (0, 0), Direction.W),
                          ])
def test_direction_from_coordinates(start_coordinates, stop_coordinates, output_direction):
    """
    Test direction is calculated correctly from coordinates.
    """
    direction = get_direction_from_coordinates(start_coordinates, stop_coordinates)
    assert direction == output_direction


@pytest.mark.parametrize(("input_coordinates", "input_direction"),
                         [((6, 8), Direction.N),
                         ((5, 9), Direction.E),
                         ((6, 10), Direction.S),
                         ((7, 9), Direction.W),
                          ])
def test_robots_dont_change_direction_on_rotating_belts_after_move_card(input_coordinates, input_direction):
    """
    Test robot's direction isn't changed after he is moved by card to
    rotating conveyor belt.
    """
    robot = Robot(input_direction, input_coordinates, "tester")
    robot.program = [MovementCard(100, 1)]
    board = get_board("maps/test_belts.json")
    state = State(board, [robot])
    robot.program[0].apply_effect(robot, state)
    state.apply_all_effects(1)
    assert robot.direction == input_direction


@pytest.mark.parametrize(("input_coordinates_1", "input_coordinates_2", "output_coordinates_1", "output_coordinates_2"),
                         [((1, 10), (2, 10), (2, 10), (2, 11)),
                         ((6, 4), (7, 4), (7, 4), (7, 5)),
                         ((2, 5), (2, 4), (2, 5), (2, 4)),
                         ((2, 1), (2, 0), (2, 2), (2, 1)),
                          ])
def test_two_robots_movements_on_belts(input_coordinates_1, input_coordinates_2, output_coordinates_1, output_coordinates_2):
    """
    Test movement of two robots in a row on belts.
    """
    robots = [Robot(Direction.N, input_coordinates_1, "tester"),
              Robot(Direction.N, input_coordinates_2, "tester"),
              ]
    board = get_board("maps/test_belts.json")
    state = State(board, robots)
    state.apply_all_effects(1)
    assert robots[0].coordinates == output_coordinates_1
    assert robots[1].coordinates == output_coordinates_2


@pytest.mark.parametrize(("input_coordinates_1", "input_coordinates_2", "output_coordinates_1", "output_coordinates_2"),
                         [((5, 7), (7, 7), (5, 7), (7, 7)),
                          ])
def test_two_robots_movement_on_T_crossroad(input_coordinates_1, input_coordinates_2, output_coordinates_1, output_coordinates_2):
    """
    Test movement of two robots on T crossroads. Robots are facing each other
    across the crossroad. Both want to go through this crossroad, but none them
    move.
    """
    robots = [Robot(Direction.N, input_coordinates_1, "tester"),
              Robot(Direction.N, input_coordinates_2, "tester"),
              ]
    board = get_board("maps/test_belts.json")
    state = State(board, robots)
    state.apply_all_effects(1)
    assert robots[0].coordinates == output_coordinates_1
    assert robots[1].coordinates == output_coordinates_2


@pytest.mark.parametrize(("input_coordinates_1", "input_coordinates_2", "output_coordinates_1", "output_coordinates_2"),
                         [((3, 10), (3, 11), (3, 10), (3, 11)),
                         ((6, 9), (7, 9), (6, 9), (7, 9)),
                         ((4, 3), (5, 2), (5, 3), (5, 2)),
                         ((2, 0), (2, 2), (2, 1), (2, 2)),
                          ])
def test_robot_does_not_move_onto_another_robot(input_coordinates_1, input_coordinates_2, output_coordinates_1, output_coordinates_2):
    """
    Test robot doesn't move to coordinates of other robot. Other robot stands
    on the end of belt but on the ground tile.
    """
    robots = [Robot(Direction.N, input_coordinates_1, "tester"),
              Robot(Direction.N, input_coordinates_2, "tester"),
              ]
    board = get_board("maps/test_belts.json")
    state = State(board, robots)
    state.apply_all_effects(1)
    assert robots[0].coordinates == output_coordinates_1
    assert robots[1].coordinates == output_coordinates_2


def test_card_priorities():
    """
    Check that robots are sorted according to their cards on hand.
    Assert first and last robot's on the list priority.
    """
    state = State.get_start_state("maps/test_effects.json")
    cards = [[MovementCard(100, 1), MovementCard(100, 1)],
             [RotationCard(120, Rotation.U_TURN), MovementCard(200, 2)],
             [MovementCard(150, -1), MovementCard(110, 1)],
             [MovementCard(110, 1), MovementCard(140, 1)],
             [RotationCard(55, Rotation.LEFT), MovementCard(250, 2)],
             [MovementCard(300, 3), MovementCard(350, 3)],
             [MovementCard(230, 2), RotationCard(80, Rotation.RIGHT)],
             [MovementCard(150, 1), MovementCard(140, 1)],
             ]
    # create robot's programs
    i = 0
    for robot in state.get_active_robots():
        robot.program = cards[i]
        i += 1

    robot_cards = state.get_robots_ordered_by_cards_priority(0)
    print(robot_cards[0])
    assert robot_cards[0][0].program[0].priority == 300
    assert robot_cards[7][0].program[0].priority == 55

    robot_cards = state.get_robots_ordered_by_cards_priority(1)
    assert robot_cards[0][0].program[1].priority == 350
    assert robot_cards[7][0].program[1].priority == 80


def test_robot_from_dict():
    """
    Check if method Robot.from_dict returns robot from JSON.
    """
    robot_description = {"robot_data": {'name': 'crazybot', 'coordinates': (10, 1),
                         'lives': 5, 'flags': 8, 'damages': 5, 'power_down': False,
                         'direction': 90, 'start_coordinates': (3, 1), 'selection_confirmed': False}}
    robot = Robot.from_dict(robot_description)
    assert robot.name == "crazybot"
    assert robot.coordinates == (10, 1)
    assert robot.lives == 5
    assert robot.flags == 8
    assert robot.damages == 5
    assert robot.power_down == False
    assert robot.direction == Direction.E
    assert robot.start_coordinates == (3, 1)
    assert robot.selection_confirmed == False


def test_state_from_dict():
    """
    Check if state.from_dict can load State from JSON.
    """
    data = {"game_state": {'board': {'height': 12, 'infinite': False, 'layers': [{'data': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'height': 12, 'id': 1, 'name': 'layer 1', 'opacity': 1, 'type': 'tilelayer', 'visible': True, 'width': 12, 'x': 0, 'y': 0}, {'data': [0, 2684354573, 0, 2684354573, 0, 2684354573, 2684354573, 0, 2684354573, 0, 2684354573, 38, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3221225485, 0, 0, 0, 2684354578, 0, 2684354578, 0, 38, 1610612754, 0, 0, 0, 13, 0, 2684354578, 33, 2684354578, 0, 2, 1610612754, 0, 1610612754, 0, 3221225485, 0, 0, 2, 2684354578, 0, 39, 30, 0, 1610612754, 0, 0, 0, 13, 0, 2684354578, 0, 2684354578, 0, 0, 1610612754, 32, 1610612754, 0, 3221225485, 0, 0, 31, 2684354578, 0, 2684354578, 0, 0, 1610612754, 2, 0, 0, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3221225485, 38, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 40, 41, 0, 42, 0, 43, 44, 0, 45, 0, 46, 47, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'height': 12, 'id': 2, 'name': 'layer 2', 'opacity': 1, 'type': 'tilelayer', 'visible': True, 'width': 12, 'x': 0, 'y': 0}, {'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 25, 2684354584, 2684354584, 2684354584, 2684354584, 2684354584, 2684354584, 2684354584, 2684354584, 2684354585, 0, 0, 24, 0, 2684354573, 0, 2684354573, 2684354573, 0, 2684354573, 0, 3221225496, 0, 0, 24, 13, 0, 0, 0, 0, 0, 0, 3221225485, 3221225496, 0, 0, 24, 0, 0, 0, 0, 0, 0, 0, 0, 3221225496, 0, 0, 24, 13, 0, 0, 0, 0, 0, 0, 3221225485, 3221225496, 0, 0, 24, 0, 1610612749, 0, 1610612749, 1610612749, 0, 1610612749, 0, 3221225496, 0, 0, 1610612761, 1610612760, 1610612760, 1610612760, 1610612760, 1610612760, 1610612760, 1610612760, 1610612760, 3221225497, 0, 0, 0, 1610612749, 0, 1610612749, 0, 0, 1610612749, 13, 1610612749, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 13, 0, 0, 13, 0, 13, 0, 13, 13, 13, 0, 13, 0, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'height': 12, 'id': 3, 'name': 'layer 3', 'opacity': 1, 'type': 'tilelayer', 'visible': True, 'width': 12, 'x': 0, 'y': 0}], 'nextlayerid': 5, 'nextobjectid': 1, 'orientation': 'orthogonal', 'renderorder': 'right-up', 'tiledversion': '1.2.1', 'tileheight': 64, 'tilesets': [{'firstgid': 1, 'source': 'development_tileset.json'}], 'tilewidth': 64, 'type': 'map', 'version': 1.2, 'width': 12}, 'robots': [{'robot_data': {'name': 'hanka', 'coordinates': (0, 1), 'lives': 3, 'flags': 0, 'damages': 0, 'power_down': False, 'direction': 0, 'start_coordinates': (0, 1), 'selection_confirmed': False}}, {'robot_data': {'name': 'ivet', 'coordinates': (1, 1), 'lives': 3, 'flags': 0, 'damages': 4, 'power_down': False, 'direction': 0, 'start_coordinates': (1, 1), 'selection_confirmed': False}}]}}
    state = State.from_dict(data)
    assert state.robots[0].coordinates == (0, 1)
    assert state.robots[1].damages == 4
    assert state._board[0, 11][0].direction == Direction.N
    assert state._board[2, 5][0].name == "ground"


def test_get_robot_names():
    """
    Get_robot_names return correct robot names.
    Names - names of the files with robots avatars.
    """
    robot_names = get_robot_names()
    assert robot_names[0] == "bender"
    assert robot_names[1] == "bishop"
    assert robot_names[2] == "cyberbot"
    assert robot_names[3] == "kitt"
    assert robot_names[4] == "marvin"
    assert robot_names[5] == "mintbot"
    assert robot_names[6] == "robbie"
    assert robot_names[7] == "rusty"
