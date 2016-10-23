import pytest

from map.predefined.vanilla_dip import generate_map
from player.command.command import ConvoyTransportCommand, MoveCommand, HoldCommand, SupportCommand, ConvoyMoveCommand
from player.player import Player
from player.unit import UnitTypes
from turn.convoy.check_chains import convoy_chain_exists

def test_error_if_not_convoy_move_command():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'St. Petersburg', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("Russia", map, starting_configuration)
    commands = [
        MoveCommand(player, player.units[0], 'Finland'),
    ]

    with pytest.raises(AssertionError):
        convoy_chain_exists(map, commands[0], commands)

def test_fail_if_no_transport_commands():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'St. Petersburg', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("Russia", map, starting_configuration)
    commands = [
        ConvoyMoveCommand(player, player.units[0], 'Sweden'),
    ]

    assert not convoy_chain_exists(map, commands[0], commands)

def test_fail_if_no_adjacent_transport_commands():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'St. Petersburg', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Baltic Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Russia", map, starting_configuration)
    commands = [
        ConvoyMoveCommand(player, player.units[0], 'Sweden'),
        ConvoyTransportCommand(player, player.units[1], player.units[0], 'Sweden'),
    ]

    assert not convoy_chain_exists(map, commands[0], commands)

def test_fail_if_adjacent_transport_command_disagrees_on_destination():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'St. Petersburg', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Gulf of Bothnia', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Russia", map, starting_configuration)
    commands = [
        ConvoyMoveCommand(player, player.units[0], 'Sweden'),
        ConvoyTransportCommand(player, player.units[1], player.units[0], 'Livonia'),
    ]

    assert not convoy_chain_exists(map, commands[0], commands)

def test_fail_if_transport_chain_not_long_enough():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'St. Petersburg', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Gulf of Bothnia', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Russia", map, starting_configuration)
    commands = [
        ConvoyMoveCommand(player, player.units[0], 'Denmark'),
        ConvoyTransportCommand(player, player.units[1], player.units[0], 'Denmark'),
    ]

    assert not convoy_chain_exists(map, commands[0], commands)

def test_succeed_for_transport_chain_of_length_one():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'St. Petersburg', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Gulf of Bothnia', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Russia", map, starting_configuration)
    commands = [
        ConvoyMoveCommand(player, player.units[0], 'Sweden'),
        ConvoyTransportCommand(player, player.units[1], player.units[0], 'Sweden'),
    ]

    assert convoy_chain_exists(map, commands[0], commands)

def test_succeed_for_transport_chain_of_length_two():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'St. Petersburg', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Gulf of Bothnia', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Baltic Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Russia", map, starting_configuration)
    commands = [
        ConvoyMoveCommand(player, player.units[0], 'Denmark'),
        ConvoyTransportCommand(player, player.units[1], player.units[0], 'Denmark'),
        ConvoyTransportCommand(player, player.units[2], player.units[0], 'Denmark'),
    ]

    assert convoy_chain_exists(map, commands[0], commands)

def test_succeed_for_transport_chain_with_multiple_possible_paths():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'Wales', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'English Channel', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Irish Sea', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'North Atlantic Ocean', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Norwegian Sea', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'North Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Russia", map, starting_configuration)
    commands = [
        ConvoyMoveCommand(player, player.units[0], 'Norway'),
        ConvoyTransportCommand(player, player.units[1], player.units[0], 'Norway'),
        ConvoyTransportCommand(player, player.units[2], player.units[0], 'Norway'),
        ConvoyTransportCommand(player, player.units[3], player.units[0], 'Norway'),
        ConvoyTransportCommand(player, player.units[4], player.units[0], 'Norway'),
        ConvoyTransportCommand(player, player.units[5], player.units[0], 'Norway'),
    ]

    assert convoy_chain_exists(map, commands[0], commands)

def test_fail_for_lengthy_chain_that_does_not_lead_to_destination():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'Wales', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'English Channel', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Irish Sea', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'North Atlantic Ocean', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Norwegian Sea', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'North Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Russia", map, starting_configuration)
    commands = [
        ConvoyMoveCommand(player, player.units[0], 'Norway'),
        ConvoyTransportCommand(player, player.units[1], player.units[0], 'Tuscany'),
        ConvoyTransportCommand(player, player.units[2], player.units[0], 'Tuscany'),
        ConvoyTransportCommand(player, player.units[3], player.units[0], 'Tuscany'),
        ConvoyTransportCommand(player, player.units[4], player.units[0], 'Tuscany'),
        ConvoyTransportCommand(player, player.units[5], player.units[0], 'Tuscany'),
    ]

    assert not convoy_chain_exists(map, commands[0], commands)