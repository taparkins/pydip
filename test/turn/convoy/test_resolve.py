from map.predefined.vanilla_dip import generate_map
from player.command.command import ConvoyTransportCommand, MoveCommand, HoldCommand, ConvoyMoveCommand
from player.player import Player
from player.unit import UnitTypes
from turn.convoy.resolve import simplify_convoy_commands

def test_no_change_for_empty_commands_list():
    map = generate_map()
    assert simplify_convoy_commands(map, []) == []

def test_no_change_for_no_convoy_commands():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'Adriatic Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Italy", map, starting_configuration)
    commands = [
        MoveCommand(player, player.units[0], 'Apulia Coast'),
    ]

    assert simplify_convoy_commands(map, commands) == commands

def test_convert_transport_to_hold_for_no_associated_move():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'Trieste', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Adriatic Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Italy", map, starting_configuration)
    commands = [
        MoveCommand(player, player.units[0], 'Venice'),
        ConvoyTransportCommand(player, player.units[1], player.units[0], 'Apulia'),
    ]

    assert simplify_convoy_commands(map, commands) == [
        commands[0],
        HoldCommand(player, player.units[1]),
    ]

def test_convert_move_to_hold_for_no_associated_transport():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'Trieste', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Adriatic Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Italy", map, starting_configuration)
    commands = [
        ConvoyMoveCommand(player, player.units[0], 'Apulia'),
        HoldCommand(player, player.units[1]),
    ]

    assert simplify_convoy_commands(map, commands) == [
        HoldCommand(player, player.units[0]),
        commands[1],
    ]

def test_convert_convoy_to_holds_for_cut_convoy():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'Trieste', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Adriatic Sea', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Ionian Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Italy", map, starting_configuration)
    commands = [
        ConvoyMoveCommand(player, player.units[0], 'Apulia'),
        ConvoyTransportCommand(player, player.units[1], player.units[0], 'Apulia'),
        MoveCommand(player, player.units[2], 'Adriatic Sea'),
    ]

    assert simplify_convoy_commands(map, commands) == [
        HoldCommand(player, player.units[0]),
        HoldCommand(player, player.units[1]),
        commands[2],
    ]

def test_convert_convoy_to_holds_for_incomplete_convoy_chain():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'Trieste', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Adriatic Sea', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Ionian Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Italy", map, starting_configuration)
    commands = [
        ConvoyMoveCommand(player, player.units[0], 'North Africa'),
        ConvoyTransportCommand(player, player.units[1], player.units[0], 'North Africa'),
        ConvoyTransportCommand(player, player.units[2], player.units[0], 'North Africa'),
    ]

    assert simplify_convoy_commands(map, commands) == [
        HoldCommand(player, player.units[0]),
        HoldCommand(player, player.units[1]),
        HoldCommand(player, player.units[2]),
    ]

def test_no_conversion_for_multiple_fleet_convoy_chain():
    map = generate_map()
    starting_configuration = [
        {'territory_name': 'Trieste', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Adriatic Sea', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Ionian Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Italy", map, starting_configuration)
    commands = [
        ConvoyMoveCommand(player, player.units[0], 'Tunis'),
        ConvoyTransportCommand(player, player.units[1], player.units[0], 'Tunis'),
        ConvoyTransportCommand(player, player.units[2], player.units[0], 'Tunis'),
    ]

    assert simplify_convoy_commands(map, commands) == commands