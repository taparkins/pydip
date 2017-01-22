from pydip.map.predefined.vanilla_dip import generate_map
from pydip.player.command.command import (
    ConvoyMoveCommand,
    ConvoyTransportCommand,
    HoldCommand,
    MoveCommand,
    SupportCommand,
)
from pydip.player.player import Player
from pydip.player.unit import UnitTypes
from pydip.turn.command_map import CommandMap


# noinspection PyProtectedMember
def test__move_command():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Smyrna', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("Turkey", game_map, starting_configuration)
    command = MoveCommand(player, player.units[0], 'Ankara')
    command_map = CommandMap(game_map, [command])

    assert command_map._home_map            == {'Smyrna' : command}
    assert command_map._attacker_map        == {'Ankara' : [command]}
    assert command_map._convoy_attacker_map == dict()
    assert command_map._transport_map       == dict()
    assert command_map._support_map         == dict()


# noinspection PyProtectedMember
def test__hold_command():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Smyrna', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("Turkey", game_map, starting_configuration)
    command = HoldCommand(player, player.units[0])
    command_map = CommandMap(game_map, [command])

    assert command_map._home_map            == {'Smyrna' : command}
    assert command_map._attacker_map        == {'Smyrna' : [command]}
    assert command_map._convoy_attacker_map == dict()
    assert command_map._transport_map       == dict()
    assert command_map._support_map         == dict()


# noinspection PyProtectedMember
def test__support_command():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Smyrna', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Armenia Coast', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Serbia', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Greece', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("Turkey", game_map, starting_configuration)
    move_command = MoveCommand(player, player.units[0], 'Ankara')
    hold_command = HoldCommand(player, player.units[2])
    support_command_1 = SupportCommand(player, player.units[1], player.units[0], 'Ankara')
    support_command_2 = SupportCommand(player, player.units[3], player.units[2], 'Serbia')
    command_map = CommandMap(game_map, [move_command, support_command_1, hold_command, support_command_2])

    assert command_map._home_map == {
        'Smyrna' : move_command,
        'Armenia' : support_command_1,
        'Serbia' : hold_command,
        'Greece' : support_command_2,
    }
    assert command_map._attacker_map == {
        'Ankara' : [move_command],
        'Serbia' : [hold_command],
    }
    assert command_map._convoy_attacker_map == dict()
    assert command_map._transport_map       == dict()
    assert command_map._support_map == {
        ('Smyrna', 'Ankara') : [support_command_1],
        ('Serbia', 'Serbia') : [support_command_2],
    }


# noinspection PyProtectedMember
def test__convoy_move_command():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Ankara', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("Turkey", game_map, starting_configuration)
    command = ConvoyMoveCommand(player, player.units[0], 'Sevastopol')
    command_map = CommandMap(game_map, [command])

    assert command_map._home_map            == {'Ankara' : command}
    assert command_map._attacker_map        == dict()
    assert command_map._convoy_attacker_map == {'Sevastopol' : [command]}
    assert command_map._transport_map       == dict()
    assert command_map._support_map         == dict()


# noinspection PyProtectedMember
def test__convoy_transport_command():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Ankara', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Black Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Turkey", game_map, starting_configuration)
    move_command = ConvoyMoveCommand(player, player.units[0], 'Sevastopol')
    transport_command = ConvoyTransportCommand(player, player.units[1], player.units[0], 'Sevastopol')
    command_map = CommandMap(game_map, [move_command, transport_command])

    assert command_map._home_map            == {'Ankara' : move_command, 'Black Sea' : transport_command}
    assert command_map._attacker_map        == dict()
    assert command_map._convoy_attacker_map == {'Sevastopol' : [move_command]}
    assert command_map._transport_map       == {('Ankara', 'Sevastopol') : [transport_command]}
    assert command_map._support_map         == dict()


# noinspection PyProtectedMember
def test__several_commands():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Ankara', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Black Sea', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Budapest', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Rumania Coast', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Ukraine', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Moscow', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("Turkey", game_map, starting_configuration)

    commands = [
        ConvoyMoveCommand(player, player.units[0], 'Sevastopol'),
        ConvoyTransportCommand(player, player.units[1], player.units[0], 'Sevastopol'),
        MoveCommand(player, player.units[2], 'Rumania'),
        MoveCommand(player, player.units[3], 'Sevastopol Coast'),
        SupportCommand(player, player.units[4], player.units[3], 'Sevastopol Coast'),
        MoveCommand(player, player.units[5], 'Sevastopol'),
    ]
    command_map = CommandMap(game_map, commands)

    assert command_map._home_map == {
        'Ankara'    : commands[0],
        'Black Sea' : commands[1],
        'Budapest'  : commands[2],
        'Rumania'   : commands[3],
        'Ukraine'   : commands[4],
        'Moscow'    : commands[5],
    }
    assert command_map._attacker_map == {
        'Rumania'    : [commands[2]],
        'Sevastopol' : [commands[3], commands[5]],
    }
    assert command_map._convoy_attacker_map == {
        'Sevastopol' : [commands[0]],
    }
    assert command_map._transport_map == {
        ('Ankara', 'Sevastopol') : [commands[1]],
    }
    assert command_map._support_map == {
        ('Rumania', 'Sevastopol') : [commands[4]],
    }
