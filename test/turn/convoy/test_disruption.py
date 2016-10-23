import pytest

from map.predefined.vanilla_dip import generate_map
from player.command.command import ConvoyTransportCommand, MoveCommand, HoldCommand, SupportCommand
from player.player import Player
from player.unit import UnitTypes
from turn.convoy.disruption import convoy_is_disrupted

def test_fail_for_non_convoy_transport_command():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'Adriatic Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Italy", map, starting_configuration)
    commands = [
        MoveCommand(player, player.units[0], 'Apulia Coast'),
    ]

    with pytest.raises(AssertionError):
        convoy_is_disrupted(commands[0], commands)

def test_no_cut_for_no_other_commands():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'Albania', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Adriatic Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Italy", map, starting_configuration)
    commands = [
        ConvoyTransportCommand(player, player.units[1], player.units[0], 'Apulia'),
    ]

    assert not convoy_is_disrupted(commands[0], commands)

def test_no_cut_for_no_move_commands():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'Albania', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Adriatic Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Italy", map, starting_configuration)
    commands = [
        ConvoyTransportCommand(player, player.units[1], player.units[0], 'Apulia'),
        SupportCommand(player, player.units[0], player.units[1], 'Trieste Coast'),
    ]

    assert not convoy_is_disrupted(commands[0], commands)

def test_no_cut_for_no_conflicting_move_commands():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'Albania', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Adriatic Sea', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Ionian Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Italy", map, starting_configuration)
    commands = [
        ConvoyTransportCommand(player, player.units[1], player.units[0], 'Apulia'),
        HoldCommand(player, player.units[0]),
        MoveCommand(player, player.units[2], 'Aegean Sea'),
    ]

    assert not convoy_is_disrupted(commands[0], commands)

def test_cut_convoy_transport():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'Albania', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Adriatic Sea', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Ionian Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Italy", map, starting_configuration)
    commands = [
        ConvoyTransportCommand(player, player.units[1], player.units[0], 'Apulia'),
        MoveCommand(player, player.units[2], 'Adriatic Sea'),
    ]

    assert convoy_is_disrupted(commands[0], commands)