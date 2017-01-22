import pytest

from pydip.map.predefined.vanilla_dip import generate_map
from pydip.player.command.command import ConvoyTransportCommand
from pydip.player.player import Player
from pydip.player.unit import UnitTypes


def test_convoy_transport_fails_for_troop_transporting():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Apulia', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Rome', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("Italy", game_map, starting_configuration)

    with pytest.raises(AssertionError):
        ConvoyTransportCommand(player, player.units[0], player.units[1], 'Marseilles')


def test_convoy_transport_fails_for_fleet_moving():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Spain South Coast', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Western Mediterranean Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("France", game_map, starting_configuration)

    with pytest.raises(AssertionError):
        ConvoyTransportCommand(player, player.units[0], player.units[1], 'Tunis')


def test_convoy_transport_fails_for_landlocked_origin():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Tyrrhenian Sea', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Bohemia', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("Germany", game_map, starting_configuration)

    with pytest.raises(AssertionError):
        ConvoyTransportCommand(player, player.units[0], player.units[1], 'Rome')


def test_convoy_transport_fails_for_landlocked_destination():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Tyrrhenian Sea', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Naples', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("Italy", game_map, starting_configuration)

    with pytest.raises(AssertionError):
        ConvoyTransportCommand(player, player.units[0], player.units[1], 'Warsaw')


def test_convoy_transport_success():
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Tyrrhenian Sea', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Constantinople', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("Turkey", game_map, starting_configuration)

    command = ConvoyTransportCommand(player, player.units[0], player.units[1], 'Tunis')

    assert command.unit.position == 'Tyrrhenian Sea'
    assert command.transported_unit.position == 'Constantinople'
    assert command.destination == 'Tunis'
