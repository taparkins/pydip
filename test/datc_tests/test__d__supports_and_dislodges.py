import pytest

from map.predefined.vanilla_dip import generate_map
from player.command.command import MoveCommand, SupportCommand, HoldCommand, ConvoyMoveCommand, ConvoyTransportCommand
from player.player import Player
from player.unit import Unit, UnitTypes
from turn.resolve import resolve_turn


def test_d_1__supported_hold_can_prevent_dislodgement():
    """
    AUSTRIA: A Trieste -> Venice
             F Adriatic Sea Supports Trieste -> Venice

    ITALY:   A Venice Hold
             A Tyrolia Supports Venice Hold
    """
    map = generate_map()
    austria_starting_configuration = [
        {'territory_name': 'Trieste', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Adriatic Sea', 'unit_type': UnitTypes.FLEET},
    ]
    austria = Player("Austria", map, austria_starting_configuration)

    italy_starting_configuration = [
        {'territory_name': 'Venice', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Tyrolia', 'unit_type': UnitTypes.TROOP},
    ]
    italy = Player("Italy", map, italy_starting_configuration)

    commands = [
        MoveCommand(austria, austria.units[0], 'Venice'),
        SupportCommand(austria, austria.units[1], austria.units[0], 'Venice'),

        HoldCommand(italy, italy.units[0]),
        SupportCommand(italy, italy.units[1], italy.units[0], 'Venice'),
    ]
    result = resolve_turn(map, commands)
    assert result == {
        'Austria': {
            Unit(UnitTypes.FLEET, 'Adriatic Sea'): None,
            Unit(UnitTypes.TROOP, 'Trieste'): None,
        },
        'Italy': {
            Unit(UnitTypes.TROOP, 'Venice'): None,
            Unit(UnitTypes.TROOP, 'Tyrolia'): None,
        },
    }

def test_d_2__move_cuts_support_on_hold():
    """
    AUSTRIA: A Trieste -> Venice
             F Adriatic Sea Supports Trieste -> Venice
             A Vienna -> Tyrolia

    ITALY:   A Venice Hold
             A Tyrolia Supports Venice Hold
    """
    map = generate_map()
    austria_starting_configuration = [
        {'territory_name': 'Trieste', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Adriatic Sea', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Vienna', 'unit_type': UnitTypes.TROOP},
    ]
    austria = Player("Austria", map, austria_starting_configuration)

    italy_starting_configuration = [
        {'territory_name': 'Venice', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Tyrolia', 'unit_type': UnitTypes.TROOP},
    ]
    italy = Player("Italy", map, italy_starting_configuration)

    commands = [
        MoveCommand(austria, austria.units[0], 'Venice'),
        SupportCommand(austria, austria.units[1], austria.units[0], 'Venice'),
        MoveCommand(austria, austria.units[2], 'Tyrolia'),

        HoldCommand(italy, italy.units[0]),
        SupportCommand(italy, italy.units[1], italy.units[0], 'Venice'),
    ]
    result = resolve_turn(map, commands)
    assert result == {
        'Austria': {
            Unit(UnitTypes.FLEET, 'Adriatic Sea'): None,
            Unit(UnitTypes.TROOP, 'Venice'): None,
            Unit(UnitTypes.TROOP, 'Vienna'): None,
        },
        'Italy': {
            Unit(UnitTypes.TROOP, 'Venice'): {
                'Piedmont',
                'Tuscany',
                'Rome',
                'Apulia',
            },
            Unit(UnitTypes.TROOP, 'Tyrolia'): None,
        },
    }

def test_d_3__move_cuts_support_on_move():
    """
    AUSTRIA: A Trieste -> Venice
             F Adriatic Sea Supports Trieste -> Venice

    ITALY:   A Venice Hold
             F Ionian Sea -> Adriatic Sea
    """
    map = generate_map()
    austria_starting_configuration = [
        {'territory_name': 'Trieste', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Adriatic Sea', 'unit_type': UnitTypes.FLEET},
    ]
    austria = Player("Austria", map, austria_starting_configuration)

    italy_starting_configuration = [
        {'territory_name': 'Venice', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Ionian Sea', 'unit_type': UnitTypes.FLEET},
    ]
    italy = Player("Italy", map, italy_starting_configuration)
    commands = [
        MoveCommand(austria, austria.units[0], 'Venice'),
        SupportCommand(austria, austria.units[1], austria.units[0], 'Venice'),

        HoldCommand(italy, italy.units[0]),
        MoveCommand(italy, italy.units[1], 'Adriatic Sea'),
    ]

    result = resolve_turn(map, commands)
    assert result == {
        'Austria': {
            Unit(UnitTypes.FLEET, 'Adriatic Sea'): None,
            Unit(UnitTypes.TROOP, 'Trieste'): None,
        },
        'Italy': {
            Unit(UnitTypes.TROOP, 'Venice'): None,
            Unit(UnitTypes.FLEET, 'Ionian Sea'): None,
        },
    }

def test_d_4__support_to_hold_unit_supporting_hold_allowed():
    """
    GERMANY: A Berlin Supports Kiel Coast Hold
             F Kiel Coast Supports Berlin Hold

    RUSSIA:  A Prussia -> Berlin
             F Baltic Sea Supports Prussia -> Berlin
    """
    map = generate_map()
    germany_starting_configuration = [
        {'territory_name': 'Berlin', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Kiel Coast', 'unit_type': UnitTypes.FLEET},
    ]
    germany = Player("Germany", map, germany_starting_configuration)

    russia_starting_configuration = [
        {'territory_name': 'Prussia', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Baltic Sea', 'unit_type': UnitTypes.FLEET},
    ]
    russia = Player("Russia", map, russia_starting_configuration)
    commands = [
        SupportCommand(germany, germany.units[0], germany.units[1], 'Kiel Coast'),
        SupportCommand(germany, germany.units[1], germany.units[0], 'Berlin'),

        MoveCommand(russia, russia.units[0], 'Berlin'),
        SupportCommand(russia, russia.units[1], russia.units[0], 'Berlin'),
    ]

    result = resolve_turn(map, commands)
    assert result == {
        'Germany': {
            Unit(UnitTypes.FLEET, 'Kiel Coast'): None,
            Unit(UnitTypes.TROOP, 'Berlin'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Prussia'): None,
            Unit(UnitTypes.FLEET, 'Baltic Sea'): None,
        },
    }

def test_d_5__support_to_hold_unit_supporting_move_allowed():
    """
    GERMANY: A Munich -> Silesia
             A Berlin Supports Munich -> Silesia
             F Kiel Coast Supports Berlin Hold

    RUSSIA:  A Prussia -> Berlin
             F Baltic Sea Supports Prussia -> Berlin
    """
    map = generate_map()
    germany_starting_configuration = [
        {'territory_name': 'Munich', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Berlin', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Kiel Coast', 'unit_type': UnitTypes.FLEET},
    ]
    germany = Player("Germany", map, germany_starting_configuration)

    russia_starting_configuration = [
        {'territory_name': 'Prussia', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Baltic Sea', 'unit_type': UnitTypes.FLEET},
    ]
    russia = Player("Russia", map, russia_starting_configuration)
    commands = [
        MoveCommand(germany, germany.units[0], 'Silesia'),
        SupportCommand(germany, germany.units[1], germany.units[0], 'Silesia'),
        SupportCommand(germany, germany.units[2], germany.units[1], 'Berlin'),

        MoveCommand(russia, russia.units[0], 'Berlin'),
        SupportCommand(russia, russia.units[1], russia.units[0], 'Berlin'),
    ]

    result = resolve_turn(map, commands)
    assert result == {
        'Germany': {
            Unit(UnitTypes.FLEET, 'Kiel Coast'): None,
            Unit(UnitTypes.TROOP, 'Berlin'): None,
            Unit(UnitTypes.TROOP, 'Silesia'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Prussia'): None,
            Unit(UnitTypes.FLEET, 'Baltic Sea'): None,
        },
    }

def test_d_6__support_to_hold_on_convoying_unit_allowed():
    """
    GERMANY: A Berlin -> Sweden (Convoy)
             F Baltic Sea Transports Berlin -> Sweden
             F Prussia Coast Supports Baltic Sea Hold

    RUSSIA:  F Livonia Coast -> Baltic Sea
             F Gulf of Bothnia Supports Livonia Coast -> Baltic Sea
    """
    map = generate_map()
    germany_starting_configuration = [
        {'territory_name': 'Berlin', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Baltic Sea', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Prussia Coast', 'unit_type': UnitTypes.FLEET},
    ]
    germany = Player("Germany", map, germany_starting_configuration)

    russia_starting_configuration = [
        {'territory_name': 'Livonia Coast', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Gulf of Bothnia', 'unit_type': UnitTypes.FLEET},
    ]
    russia = Player("Russia", map, russia_starting_configuration)
    commands = [
        ConvoyMoveCommand(germany, germany.units[0], 'Sweden'),
        ConvoyTransportCommand(germany, germany.units[1], germany.units[0], 'Sweden'),
        SupportCommand(germany, germany.units[2], germany.units[1], 'Baltic Sea'),

        MoveCommand(russia, russia.units[0], 'Baltic Sea'),
        SupportCommand(russia, russia.units[1], russia.units[0], 'Baltic Sea'),
    ]

    result = resolve_turn(map, commands)
    assert result == {
        'Germany': {
            Unit(UnitTypes.FLEET, 'Baltic Sea'): None,
            Unit(UnitTypes.FLEET, 'Prussia Coast'): None,
            Unit(UnitTypes.TROOP, 'Sweden'): None,
        },
        'Russia': {
            Unit(UnitTypes.FLEET, 'Livonia Coast'): None,
            Unit(UnitTypes.FLEET, 'Gulf of Bothnia'): None,
        },
    }

def test_d_7__support_to_hold_on_moving_unit_not_allowed():
    """
    GERMANY: F Baltic Sea -> Sweden Coast
             F Prussia Coast Supports Baltic Sea Hold

    RUSSIA:  F Livonia Coast -> Baltic Sea
             F Gulf of Bothnia Supports Livonia Coast -> Baltic Sea
             A Finland -> Sweden
    """
    map = generate_map()
    germany_starting_configuration = [
        {'territory_name': 'Baltic Sea', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Prussia Coast', 'unit_type': UnitTypes.FLEET},
    ]
    germany = Player("Germany", map, germany_starting_configuration)

    russia_starting_configuration = [
        {'territory_name': 'Livonia Coast', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Gulf of Bothnia', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Finland', 'unit_type': UnitTypes.TROOP},
    ]
    russia = Player("Russia", map, russia_starting_configuration)
    commands = [
        MoveCommand(germany, germany.units[0], 'Sweden Coast'),
        SupportCommand(germany, germany.units[1], germany.units[0], 'Baltic Sea'),

        MoveCommand(russia, russia.units[0], 'Baltic Sea'),
        SupportCommand(russia, russia.units[1], russia.units[0], 'Baltic Sea'),
        MoveCommand(russia, russia.units[2], 'Sweden'),
    ]

    result = resolve_turn(map, commands)
    assert result == {
        'Germany': {
            Unit(UnitTypes.FLEET, 'Baltic Sea'): {
                'Kiel Coast',
                'Denmark Coast',
                'Berlin Coast',
            },
            Unit(UnitTypes.FLEET, 'Prussia Coast'): None,
        },
        'Russia': {
            Unit(UnitTypes.FLEET, 'Baltic Sea'): None,
            Unit(UnitTypes.FLEET, 'Gulf of Bothnia'): None,
            Unit(UnitTypes.TROOP, 'Finland'): None,
        },
    }

def test_d_8__failed_convoy_cannot_receive_hold_support():
    """
    AUSTRIA: A Albania -> Greece
             A Serbia Supports Albania -> Greece

    TURKEY:  A Greece -> Naples (Convoy)
             A Bulgaria Supports Greece Hold
    """
    map = generate_map()
    austria_starting_configuration = [
        {'territory_name': 'Albania', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Serbia', 'unit_type': UnitTypes.TROOP},
    ]
    austria = Player("Austria", map, austria_starting_configuration)

    turkey_starting_configuration = [
        {'territory_name': 'Greece', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Bulgaria', 'unit_type': UnitTypes.TROOP},
    ]
    turkey = Player("Turkey", map, turkey_starting_configuration)
    commands = [
        MoveCommand(austria, austria.units[0], 'Greece'),
        SupportCommand(austria, austria.units[1], austria.units[0], 'Greece'),

        ConvoyMoveCommand(turkey, turkey.units[0], 'Naples'),
        SupportCommand(turkey, turkey.units[1], turkey.units[0], 'Greece'),
    ]

    result = resolve_turn(map, commands)
    assert result == {
        'Austria': {
            Unit(UnitTypes.TROOP, 'Greece'): None,
            Unit(UnitTypes.TROOP, 'Serbia'): None,
        },
        'Turkey': {
            Unit(UnitTypes.TROOP, 'Greece'): set(),
            Unit(UnitTypes.TROOP, 'Bulgaria'): None,
        },
    }

def test_d_9__support_to_move_on_holding_unit_not_allowed():
    """
    AUSTRIA: A Trieste Hold
             A Albania Supports Trieste -> Serbia

    ITALY:   A Venice -> Trieste
             A Tyrolia Supports Venice -> Trieste
    """
    map = generate_map()
    austria_starting_configuration = [
        {'territory_name': 'Trieste', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Albania', 'unit_type': UnitTypes.TROOP},
    ]
    austria = Player("Austria", map, austria_starting_configuration)

    italy_starting_configuration = [
        {'territory_name': 'Venice', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Tyrolia', 'unit_type': UnitTypes.TROOP},
    ]
    italy = Player("Italy", map, italy_starting_configuration)
    commands = [
        HoldCommand(austria, austria.units[0]),
        SupportCommand(austria, austria.units[1], austria.units[0], 'Serbia'),

        MoveCommand(italy, italy.units[0], 'Trieste'),
        SupportCommand(italy, italy.units[1], italy.units[0], 'Trieste'),
    ]

    result = resolve_turn(map, commands)
    assert result == {
        'Austria': {
            Unit(UnitTypes.TROOP, 'Trieste'): {
                'Serbia',
                'Budapest',
                'Vienna',
            },
            Unit(UnitTypes.TROOP, 'Albania'): None,
        },
        'Italy': {
            Unit(UnitTypes.TROOP, 'Trieste'): None,
            Unit(UnitTypes.TROOP, 'Tyrolia'): None,
        },
    }

def test_d_10__self_dislodgement_prohibited():
    """
    GERMANY: A Berlin Hold
             F Kiel Coast -> Berlin Coast
             A Munich Supports Kiel Coast -> Berlin Coast
    """
    map = generate_map()
    germany_starting_configuration = [
        {'territory_name': 'Berlin', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Kiel Coast', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Munich', 'unit_type': UnitTypes.TROOP},
    ]
    germany = Player("Germany", map, germany_starting_configuration)

    commands = [
        HoldCommand(germany, germany.units[0]),
        MoveCommand(germany, germany.units[1], 'Berlin Coast'),
        SupportCommand(germany, germany.units[2], germany.units[1], 'Berlin Coast'),
    ]

    result = resolve_turn(map, commands)
    assert result == {
        'Germany': {
            Unit(UnitTypes.TROOP, 'Berlin'): None,
            Unit(UnitTypes.FLEET, 'Kiel Coast'): None,
            Unit(UnitTypes.TROOP, 'Munich'): None,
        },
    }