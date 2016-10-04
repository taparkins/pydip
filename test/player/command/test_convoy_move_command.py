import pytest

from map.predefined.vanilla_dip import generate_map
from player.command.command import ConvoyMoveCommand
from player.player import Player
from player.unit import UnitTypes

def test_convoy_move_fails_for_fleet():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'St. Petersburg North Coast', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Russia", map, starting_configuration)

    with pytest.raises(AssertionError):
        ConvoyMoveCommand(player, player.units[0], 'Sweden Coast')

def test_convoy_move_fails_for_landlocked_destination():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'Wales', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("England", map, starting_configuration)

    with pytest.raises(AssertionError):
        ConvoyMoveCommand(player, player.units[0], 'Paris')

def test_convoy_move_fails_for_landlocked_origin():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'Silesia', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("England", map, starting_configuration)

    with pytest.raises(AssertionError):
        ConvoyMoveCommand(player, player.units[0], 'London')

def test_convoy_move_success():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'Constantinople', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("France", map, starting_configuration)

    command = ConvoyMoveCommand(player, player.units[0], 'Tunis')

    assert command.unit.position == 'Constantinople'
    assert command.destination == 'Tunis'
