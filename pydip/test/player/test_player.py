import pytest

from pydip.player.unit import UnitTypes, Unit
from pydip.player.player import Player
from pydip.map.predefined.vanilla_dip import generate_map


def test_player_with_no_starting_position():
    game_map = generate_map()
    starting_configuration = []
    player = Player("test player", game_map, starting_configuration)

    assert player.starting_territories == set()
    assert player.units == []


def test_player_with_one_starting_position_without_unit():
    game_map = generate_map()
    starting_configuration = [
        { 'territory_name' : 'Sevastopol', 'unit_type' : None }
    ]
    player = Player("test player", game_map, starting_configuration)

    assert player.starting_territories == { 'Sevastopol' }
    assert player.units == []


def test_player_with_one_starting_position_with_unit():
    game_map = generate_map()
    starting_configuration = [
        { 'territory_name' : 'Sevastopol', 'unit_type' : UnitTypes.TROOP }
    ]
    player = Player("test player", game_map, starting_configuration)

    assert player.starting_territories == { 'Sevastopol' }
    assert player.units == [ Unit(UnitTypes.TROOP, 'Sevastopol') ]


def test_player_invalid_for_troop_on_sea():
    game_map = generate_map()
    starting_configuration = [
        { 'territory_name' : 'Norwegian Sea', 'unit_type' : UnitTypes.TROOP }
    ]
    with pytest.raises(AssertionError):
        Player("test player", game_map, starting_configuration)


def test_player_invalid_for_troop_on_coast():
    game_map = generate_map()
    starting_configuration = [
        { 'territory_name' : 'Liverpool Coast', 'unit_type' : UnitTypes.TROOP }
    ]
    with pytest.raises(AssertionError):
        Player("test player", game_map, starting_configuration)


def test_player_invalid_for_fleet_on_land():
    game_map = generate_map()
    starting_configuration = [
        { 'territory_name' : 'Trieste', 'unit_type' : UnitTypes.FLEET }
    ]
    with pytest.raises(AssertionError):
        Player("test player", game_map, starting_configuration)


def test_player_invalid_for_invalid_starting_territory():
    game_map = generate_map()
    starting_configuration = [
        { 'territory_name' : 'Fake Territory', 'unit_type' : None }
    ]
    with pytest.raises(AssertionError):
        Player("test player", game_map, starting_configuration)


def test_player_with_coastal_starting_position_labeled_as_parent():
    game_map = generate_map()
    starting_configuration = [
        { 'territory_name': 'Sevastopol Coast', 'unit_type': UnitTypes.FLEET }
    ]
    player = Player("test player", game_map, starting_configuration)

    assert player.starting_territories == { 'Sevastopol' }
    assert player.units == [ Unit(UnitTypes.FLEET, 'Sevastopol Coast') ]


def test_player_multiple_starting_territories():
    game_map = generate_map()
    starting_configuration = [
        { 'territory_name': 'St. Petersburg North Coast', 'unit_type': UnitTypes.FLEET },
        { 'territory_name': 'Warsaw',                     'unit_type': UnitTypes.TROOP },
        { 'territory_name': 'Moscow',                     'unit_type': UnitTypes.TROOP },
        { 'territory_name': 'Sevastopol Coast',           'unit_type': UnitTypes.FLEET },
    ]

    player = Player("test player", game_map, starting_configuration)
    assert player.starting_territories == { 'St. Petersburg', 'Warsaw', 'Moscow', 'Sevastopol' }
    assert player.units == [
        Unit(UnitTypes.FLEET, 'St. Petersburg North Coast'),
        Unit(UnitTypes.TROOP, 'Warsaw'),
        Unit(UnitTypes.TROOP, 'Moscow'),
        Unit(UnitTypes.FLEET, 'Sevastopol Coast'),
    ]
