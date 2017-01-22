import pytest

from pydip.map.predefined.vanilla_dip import generate_map
from pydip.player.command.command import SupportCommand
from pydip.player.player import Player
from pydip.player.unit import UnitTypes


def test_support_destination_not_adjacent():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Trieste', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Budapest', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("Austria", game_map, starting_configuration)

    with pytest.raises(AssertionError):
        SupportCommand(player, player.units[0], player.units[1], 'Galicia')


def test_support_landlocked_destination_with_fleet():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Rumania Coast', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Serbia', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("Turkey", game_map, starting_configuration)

    with pytest.raises(AssertionError):
        SupportCommand(player, player.units[0], player.units[1], 'Budapest')


def test_support_supported_unit_not_adjacent():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Paris', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Ruhr', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("France", game_map, starting_configuration)

    command = SupportCommand(player, player.units[0], player.units[1], 'Burgundy')

    assert command.unit.position == 'Paris'
    assert command.supported_unit.position == 'Ruhr'
    assert command.destination == 'Burgundy'


def test_support_supported_unit_adjacent():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Tuscany', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Rome', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("Italy", game_map, starting_configuration)

    command = SupportCommand(player, player.units[0], player.units[1], 'Venice')

    assert command.unit.position == 'Tuscany'
    assert command.supported_unit.position == 'Rome'
    assert command.destination == 'Venice'


def test_support_troop_to_parent_of_coast_with_fleet():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Gulf of Lyon', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Tuscany', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("France", game_map, starting_configuration)

    command = SupportCommand(player, player.units[0], player.units[1], 'Piedmont')

    assert command.unit.position == 'Gulf of Lyon'
    assert command.supported_unit.position == 'Tuscany'
    assert command.destination == 'Piedmont'


def test_support_fleet_to_coast_with_troop():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Finland', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Baltic Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("France", game_map, starting_configuration)

    command = SupportCommand(player, player.units[0], player.units[1], 'Sweden Coast')

    assert command.unit.position == 'Finland'
    assert command.supported_unit.position == 'Baltic Sea'
    assert command.destination == 'Sweden Coast'


def test_support_troop_on_coast_to_another_coast():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Norway', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Norwegian Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Russia", game_map, starting_configuration)

    command = SupportCommand(player, player.units[1], player.units[0], 'Edinburgh')

    assert command.unit.position == 'Norwegian Sea'
    assert command.supported_unit.position == 'Norway'
    assert command.destination == 'Edinburgh'
