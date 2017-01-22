import pytest

from pydip.map.predefined.vanilla_dip import generate_map
from pydip.player.command.command import MoveCommand, SupportCommand, HoldCommand
from pydip.player.player import Player
from pydip.player.unit import Unit, UnitTypes
from pydip.turn.resolve import resolve_turn


def test_b_1__portugal_to_north_spain_coast():
    """
    FRANCE: F Portugal Coast -> Spain North Coast

    Adapted from original test. Original made assertions about ambiguous
    coast orders, which are not possible in this system.
    """
    game_map = generate_map()
    france_starting_configuration = [
        { 'territory_name': 'Portugal Coast', 'unit_type': UnitTypes.FLEET },
    ]
    france = Player("France", game_map, france_starting_configuration)

    commands = [
        MoveCommand(france, france.units[0], 'Spain North Coast'),
    ]
    result = resolve_turn(game_map, commands)
    assert result == {
        'France' : { Unit(UnitTypes.FLEET, 'Spain North Coast') : None },
    }


def test_b_1__portugal_to_south_spain_coast():
    """
    FRANCE: F Portugal Coast -> Spain North Coast

    Adapted from original test. Original made assertions about ambiguous
    coast orders, which are not possible in this system.
    """
    game_map = generate_map()
    france_starting_configuration = [
        {'territory_name': 'Portugal Coast', 'unit_type': UnitTypes.FLEET},
    ]
    france = Player("France", game_map, france_starting_configuration)

    commands = [
        MoveCommand(france, france.units[0], 'Spain South Coast'),
    ]
    result = resolve_turn(game_map, commands)
    assert result == {
        'France': {Unit(UnitTypes.FLEET, 'Spain South Coast'): None},
    }


def test_b_1__portugal_to_spain_mainland_disallowed():
    """
    FRANCE: F Portugal Coast -> Spain

    Adapted from original test. Original made assertions about ambiguous
    coast orders, which are not possible in this system.
    """
    game_map = generate_map()
    france_starting_configuration = [
        {'territory_name': 'Portugal Coast', 'unit_type': UnitTypes.FLEET},
    ]
    france = Player("France", game_map, france_starting_configuration)

    with pytest.raises(AssertionError):
        MoveCommand(france, france.units[0], 'Spain')


# test B.2 and B.3 are skipped, since they involve ambiguous commands which
# cannot be reproduced in this system


def test_b_4__support_to_unreachable_coast_allowed():
    """
    FRANCE: F Gascony Coast -> Spain North Coast
            F Marseilles Coast Support F Gascony Coast -> Spain North Coast
    ITALY:  F Western Mediterranean Sea -> Spain South Coast
    """
    game_map = generate_map()
    france_starting_configuration = [
        {'territory_name': 'Gascony Coast', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Marseilles Coast', 'unit_type': UnitTypes.FLEET},
    ]
    france = Player("France", game_map, france_starting_configuration)

    italy_starting_configuration = [
        {'territory_name': 'Western Mediterranean Sea', 'unit_type': UnitTypes.FLEET},
    ]
    italy = Player("Italy", game_map, italy_starting_configuration)

    commands = [
        MoveCommand(france, france.units[0], 'Spain North Coast'),
        SupportCommand(france, france.units[1], france.units[0], 'Spain North Coast'),
        MoveCommand(italy, italy.units[0], 'Spain South Coast'),
    ]
    result = resolve_turn(game_map, commands)
    assert result == {
        'France': {
            Unit(UnitTypes.FLEET, 'Spain North Coast'): None,
            Unit(UnitTypes.FLEET, 'Marseilles Coast'): None,
        },
        'Italy': {
            Unit(UnitTypes.FLEET, 'Western Mediterranean Sea'): None,
        }
    }


def test_b_5__support_from_unreachable_coast_not_allowed():
    """
    FRANCE: F Marseilles Coast -> Gulf of Lyon
            F Spain North Coast Support F Marseilles Coast -> Gulf of Lyon
    """
    game_map = generate_map()
    france_starting_configuration = [
        {'territory_name': 'Marseilles Coast', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Spain North Coast', 'unit_type': UnitTypes.FLEET},
    ]
    france = Player("France", game_map, france_starting_configuration)

    with pytest.raises(AssertionError):
        SupportCommand(france, france.units[1], france.units[0], 'Gulf of Lyon')


def test_b_6__support_can_be_cut_from_other_coast():
    """
    ENGLAND: F North Atlantic Ocean -> Mid-Atlantic Ocean
             F Irish Sea Supports North Atlantic Ocean -> Mid-Atlantic Ocean

    FRANCE:  F Mid-Atlantic Ocean Hold
             F Spain North Coast Support Mid-Atlantic Ocean Hold

    ITALY:   F Gulf of Lyon -> Spain South Coast
    """
    game_map = generate_map()
    england_starting_configuration = [
        {'territory_name': 'North Atlantic Ocean', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Irish Sea', 'unit_type': UnitTypes.FLEET},
    ]
    england = Player("England", game_map, england_starting_configuration)

    france_starting_configuration = [
        {'territory_name': 'Mid-Atlantic Ocean', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Spain North Coast', 'unit_type': UnitTypes.FLEET},
    ]
    france = Player("France", game_map, france_starting_configuration)

    italy_starting_configuration = [
        {'territory_name': 'Gulf of Lyon', 'unit_type': UnitTypes.FLEET},
    ]
    italy = Player("Italy", game_map, italy_starting_configuration)

    commands = [
        MoveCommand(england, england.units[0], 'Mid-Atlantic Ocean'),
        SupportCommand(england, england.units[1], england.units[0], 'Mid-Atlantic Ocean'),

        HoldCommand(france, france.units[0]),
        SupportCommand(france, france.units[1], france.units[0], 'Mid-Atlantic Ocean'),

        MoveCommand(italy, italy.units[0], 'Spain South Coast'),
    ]
    result = resolve_turn(game_map, commands)
    assert result == {
        'England': {
            Unit(UnitTypes.FLEET, 'Mid-Atlantic Ocean'): None,
            Unit(UnitTypes.FLEET, 'Irish Sea'): None,
        },
        'France': {
            Unit(UnitTypes.FLEET, 'Mid-Atlantic Ocean'): {
                'English Channel',
                'Brest Coast',
                'Gascony Coast',
                'Portugal Coast',
                'Western Mediterranean Sea',
                'North Africa Coast',
            },
            Unit(UnitTypes.FLEET, 'Spain North Coast'): None,
        },
        'Italy': {
            Unit(UnitTypes.FLEET, 'Gulf of Lyon'): None,
        }
    }


# Test B.7, B.8, B.9, and B.10 skipped because it involves ambiguous command that
# is not allowed in this system


def test_b_11__coast_can_not_be_ordered_to_change():
    """
    FRANCE: F Spain North Coast -> Gulf of Lyon

    Adapted from original test. Original was trying to say that entering an
    incorrect coast doesn't let you get away with anything. This system does
    not allow such a command, so this is just asserting that fact.
    """
    game_map = generate_map()
    france_starting_configuration = [
        {'territory_name': 'Spain North Coast', 'unit_type': UnitTypes.FLEET},
    ]
    france = Player("France", game_map, france_starting_configuration)

    with pytest.raises(AssertionError):
        MoveCommand(france, france.units[0], 'Gulf of Lyon')


def test_b_12__army_movement_with_coastal_specification():
    """
    FRANCE: A Gascony -> Spain North Coast
    """
    game_map = generate_map()
    france_starting_configuration = [
        {'territory_name': 'Gascony', 'unit_type': UnitTypes.TROOP},
    ]
    france = Player("France", game_map, france_starting_configuration)

    with pytest.raises(AssertionError):
        MoveCommand(france, france.units[0], 'Spain North Coast')


def test_b_13__coastal_crawl_not_allowed():
    """
    TURKEY: F Bulgaria South Coast -> Constantinople
            F Constantinople -> Bulgaria North Coast
    """
    game_map = generate_map()
    turkey_starting_configuration = [
        {'territory_name': 'Bulgaria South Coast', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Constantinople Coast', 'unit_type': UnitTypes.FLEET},
    ]
    turkey = Player("Turkey", game_map, turkey_starting_configuration)

    commands = [
        MoveCommand(turkey, turkey.units[0], 'Constantinople Coast'),
        MoveCommand(turkey, turkey.units[1], 'Bulgaria North Coast'),
    ]
    result = resolve_turn(game_map, commands)
    assert result == {
        'Turkey': {
            Unit(UnitTypes.FLEET, 'Bulgaria South Coast'): None,
            Unit(UnitTypes.FLEET, 'Constantinople Coast'): None,
        }
    }


# Test B.14 is skipped because it depends on ambiguous build command which
# is not permitted in this system
