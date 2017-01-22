import pytest

from pydip.map.predefined.vanilla_dip import generate_map
from pydip.player.command.command import HoldCommand, MoveCommand
from pydip.player.player import Player
from pydip.player.unit import UnitTypes


def test_move_not_adjacent():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Trieste', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("Austria", game_map, starting_configuration)

    with pytest.raises(AssertionError):
        MoveCommand(player, player.units[0], 'Sevastopol')


def test_move_wrong_type():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'St. Petersburg North Coast', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Russia", game_map, starting_configuration)

    with pytest.raises(AssertionError):
        MoveCommand(player, player.units[0], 'Moscow')


def test_move_land_to_land():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Paris', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("France", game_map, starting_configuration)

    command = MoveCommand(player, player.units[0], 'Brest')

    assert command.unit.position == 'Paris'
    assert command.destination == 'Brest'


def test_move_sea_to_sea():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'North Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("England", game_map, starting_configuration)

    command = MoveCommand(player, player.units[0], 'Norwegian Sea')

    assert command.unit.position == 'North Sea'
    assert command.destination == 'Norwegian Sea'


def test_move_sea_to_coast():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Adriatic Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Italy", game_map, starting_configuration)

    command = MoveCommand(player, player.units[0], 'Trieste Coast')

    assert command.unit.position == 'Adriatic Sea'
    assert command.destination == 'Trieste Coast'


def test_move_coast_to_coast():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Spain North Coast', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("France", game_map, starting_configuration)

    command = MoveCommand(player, player.units[0], 'Portugal Coast')

    assert command.unit.position == 'Spain North Coast'
    assert command.destination == 'Portugal Coast'


def test_hold():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Trieste', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("Austria", game_map, starting_configuration)

    command = HoldCommand(player, player.units[0])

    assert command.unit.position == 'Trieste'
    assert command.destination == 'Trieste'
