import pytest

from pydip.map.predefined.vanilla_dip import generate_map
from pydip.player.command.command import ConvoyMoveCommand
from pydip.player.player import Player
from pydip.player.unit import UnitTypes


def test_convoy_move_fails_for_fleet():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'St. Petersburg North Coast', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Russia", game_map, starting_configuration)

    with pytest.raises(AssertionError):
        ConvoyMoveCommand(player, player.units[0], 'Sweden Coast')


def test_convoy_move_fails_for_landlocked_destination():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Wales', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("England", game_map, starting_configuration)

    with pytest.raises(AssertionError):
        ConvoyMoveCommand(player, player.units[0], 'Paris')


def test_convoy_move_fails_for_landlocked_origin():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Silesia', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("England", game_map, starting_configuration)

    with pytest.raises(AssertionError):
        ConvoyMoveCommand(player, player.units[0], 'London')


def test_convoy_move_success():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Constantinople', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("France", game_map, starting_configuration)

    command = ConvoyMoveCommand(player, player.units[0], 'Tunis')

    assert command.unit.position == 'Constantinople'
    assert command.destination == 'Tunis'
