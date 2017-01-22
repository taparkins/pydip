from pydip.map.predefined.vanilla_dip import generate_map
from pydip.player.command.command import MoveCommand, SupportCommand, ConvoyMoveCommand, ConvoyTransportCommand
from pydip.player.player import Player
from pydip.player.unit import Unit, UnitTypes
from pydip.turn.resolve import resolve_turn


def test_c_1__three_army_circular_movement():
    """
    TURKEY: F Ankara Coast -> Constantinople Coast
            A Constantinople -> Smyrna
            A Smyrna -> Ankara
    """
    game_map = generate_map()
    turkey_starting_configuration = [
        {'territory_name': 'Ankara Coast', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Constantinople', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Smyrna', 'unit_type': UnitTypes.TROOP},
    ]
    turkey = Player("Turkey", game_map, turkey_starting_configuration)

    commands = [
        MoveCommand(turkey, turkey.units[0], 'Constantinople Coast'),
        MoveCommand(turkey, turkey.units[1], 'Smyrna'),
        MoveCommand(turkey, turkey.units[2], 'Ankara'),
    ]
    result = resolve_turn(game_map, commands)
    assert result == {
        'Turkey' : {
            Unit(UnitTypes.FLEET, 'Constantinople Coast'): None,
            Unit(UnitTypes.TROOP, 'Smyrna'): None,
            Unit(UnitTypes.TROOP, 'Ankara'): None,
        },
    }


def test_c_2__three_army_circular_movement_with_support():
    """
    TURKEY: F Ankara Coast -> Constantinople Coast
            A Constantinople -> Smyrna
            A Smyrna -> Ankara
            A Bulgaria Support Ankara Coast -> Constantinople Coast
    """
    game_map = generate_map()
    turkey_starting_configuration = [
        {'territory_name': 'Ankara Coast', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Constantinople', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Smyrna', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Bulgaria', 'unit_type': UnitTypes.TROOP},
    ]
    turkey = Player("Turkey", game_map, turkey_starting_configuration)

    commands = [
        MoveCommand(turkey, turkey.units[0], 'Constantinople Coast'),
        MoveCommand(turkey, turkey.units[1], 'Smyrna'),
        MoveCommand(turkey, turkey.units[2], 'Ankara'),
        SupportCommand(turkey, turkey.units[3], turkey.units[0], 'Constantinople Coast'),
    ]
    result = resolve_turn(game_map, commands)
    assert result == {
        'Turkey' : {
            Unit(UnitTypes.FLEET, 'Constantinople Coast'): None,
            Unit(UnitTypes.TROOP, 'Smyrna'): None,
            Unit(UnitTypes.TROOP, 'Ankara'): None,
            Unit(UnitTypes.TROOP, 'Bulgaria'): None,
        },
    }


def test_c_3__a_disrupted_three_army_circular_movement():
    """
    TURKEY: F Ankara Coast -> Constantinople Coast
            A Constantinople -> Smyrna
            A Smyrna -> Ankara
            A Bulgaria -> Constantinople
    """
    game_map = generate_map()
    turkey_starting_configuration = [
        {'territory_name': 'Ankara Coast', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Constantinople', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Smyrna', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Bulgaria', 'unit_type': UnitTypes.TROOP},
    ]
    turkey = Player("Turkey", game_map, turkey_starting_configuration)

    commands = [
        MoveCommand(turkey, turkey.units[0], 'Constantinople Coast'),
        MoveCommand(turkey, turkey.units[1], 'Smyrna'),
        MoveCommand(turkey, turkey.units[2], 'Ankara'),
        MoveCommand(turkey, turkey.units[3], 'Constantinople'),
    ]
    result = resolve_turn(game_map, commands)
    assert result == {
        'Turkey' : {
            Unit(UnitTypes.FLEET, 'Ankara Coast'): None,
            Unit(UnitTypes.TROOP, 'Smyrna'): None,
            Unit(UnitTypes.TROOP, 'Constantinople'): None,
            Unit(UnitTypes.TROOP, 'Bulgaria'): None,
        },
    }


def test_c_4__circular_movement_with_attacked_convoy():
    """
    AUSTRIA: A Trieste -> Serbia
             A Serbia -> Bulgaria

    TURKEY:  A Bulgaria -> Trieste (Convoy)
             F Aegean Sea Transports Bulgaria -> Trieste
             F Ionian Sea Transports Bulgaria -> Trieste
             F Adriatic Sea Transports Bulgaria -> Trieste

    ITALY:   F Naples Coast -> Ionian Sea
    """
    game_map = generate_map()

    austria_starting_configuration = [
        {'territory_name': 'Trieste', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Serbia', 'unit_type': UnitTypes.TROOP},
    ]
    austria = Player("Austria", game_map, austria_starting_configuration)

    turkey_starting_configuration = [
        {'territory_name': 'Bulgaria', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Aegean Sea', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Ionian Sea', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Adriatic Sea', 'unit_type': UnitTypes.FLEET},
    ]
    turkey = Player("Turkey", game_map, turkey_starting_configuration)

    italy_starting_configuration = [
        {'territory_name': 'Naples Coast', 'unit_type': UnitTypes.FLEET},
    ]
    italy = Player("Italy", game_map, italy_starting_configuration)

    commands = [
        MoveCommand(austria, austria.units[0], 'Serbia'),
        MoveCommand(austria, austria.units[1], 'Bulgaria'),

        ConvoyMoveCommand(turkey, turkey.units[0], 'Trieste'),
        ConvoyTransportCommand(turkey, turkey.units[1], turkey.units[0], 'Trieste'),
        ConvoyTransportCommand(turkey, turkey.units[2], turkey.units[0], 'Trieste'),
        ConvoyTransportCommand(turkey, turkey.units[3], turkey.units[0], 'Trieste'),

        MoveCommand(italy, italy.units[0], 'Ionian Sea'),
    ]
    result = resolve_turn(game_map, commands)
    assert result == {
        'Austria' : {
            Unit(UnitTypes.TROOP, 'Serbia'): None,
            Unit(UnitTypes.TROOP, 'Bulgaria'): None,
        },
        'Turkey' : {
            Unit(UnitTypes.TROOP, 'Trieste'): None,
            Unit(UnitTypes.FLEET, 'Aegean Sea'): None,
            Unit(UnitTypes.FLEET, 'Ionian Sea'): None,
            Unit(UnitTypes.FLEET, 'Adriatic Sea'): None,
        },
        'Italy' : {
            Unit(UnitTypes.FLEET, 'Naples Coast'): None,
        },
    }


def test_c_5__disrupted_circular_movement_due_to_dislodged_convoy():
    """
    AUSTRIA: A Trieste -> Serbia
             A Serbia -> Bulgaria

    TURKEY:  A Bulgaria -> Trieste (Convoy)
             F Aegean Sea Transports Bulgaria -> Trieste
             F Ionian Sea Transports Bulgaria -> Trieste
             F Adriatic Sea Transports Bulgaria -> Trieste

    ITALY:   F Naples Coast -> Ionian Sea
             F Tunis Coast Supports Naples Coast -> Ionian Sea
    """
    game_map = generate_map()

    austria_starting_configuration = [
        {'territory_name': 'Trieste', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Serbia', 'unit_type': UnitTypes.TROOP},
    ]
    austria = Player("Austria", game_map, austria_starting_configuration)

    turkey_starting_configuration = [
        {'territory_name': 'Bulgaria', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Aegean Sea', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Ionian Sea', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Adriatic Sea', 'unit_type': UnitTypes.FLEET},
    ]
    turkey = Player("Turkey", game_map, turkey_starting_configuration)

    italy_starting_configuration = [
        {'territory_name': 'Naples Coast', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Tunis Coast', 'unit_type': UnitTypes.FLEET},
    ]
    italy = Player("Italy", game_map, italy_starting_configuration)

    commands = [
        MoveCommand(austria, austria.units[0], 'Serbia'),
        MoveCommand(austria, austria.units[1], 'Bulgaria'),

        ConvoyMoveCommand(turkey, turkey.units[0], 'Trieste'),
        ConvoyTransportCommand(turkey, turkey.units[1], turkey.units[0], 'Trieste'),
        ConvoyTransportCommand(turkey, turkey.units[2], turkey.units[0], 'Trieste'),
        ConvoyTransportCommand(turkey, turkey.units[3], turkey.units[0], 'Trieste'),

        MoveCommand(italy, italy.units[0], 'Ionian Sea'),
        SupportCommand(italy, italy.units[1], italy.units[0], 'Ionian Sea'),
    ]
    result = resolve_turn(game_map, commands)
    assert result == {
        'Austria' : {
            Unit(UnitTypes.TROOP, 'Trieste'): None,
            Unit(UnitTypes.TROOP, 'Serbia'): None,
        },
        'Turkey' : {
            Unit(UnitTypes.TROOP, 'Bulgaria'): None,
            Unit(UnitTypes.FLEET, 'Aegean Sea'): None,
            Unit(UnitTypes.FLEET, 'Ionian Sea'): {
                'Apulia Coast',
                'Albania Coast',
                'Greece Coast',
                'Eastern Mediterranean Sea',
                'Tyrrhenian Sea',
            },
            Unit(UnitTypes.FLEET, 'Adriatic Sea'): None,
        },
        'Italy' : {
            Unit(UnitTypes.FLEET, 'Ionian Sea'): None,
            Unit(UnitTypes.FLEET, 'Tunis Coast'): None,
        },
    }


def test_c_6__two_armies_with_two_convoys():
    """
    ENGLAND: A London -> Belgium (Convoy)
             F North Sea Transports London -> Belgium

    FRANCE:  A Belgium -> London (Convoy)
             F English Channel Transports Belgium -> London
    """
    game_map = generate_map()

    england_starting_configuration = [
        {'territory_name': 'London', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'North Sea', 'unit_type': UnitTypes.FLEET},
    ]
    england = Player("England", game_map, england_starting_configuration)

    france_starting_configuration = [
        {'territory_name': 'Belgium', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'English Channel', 'unit_type': UnitTypes.FLEET},
    ]
    france = Player("France", game_map, france_starting_configuration)

    commands = [
        ConvoyMoveCommand(england, england.units[0], 'Belgium'),
        ConvoyTransportCommand(england, england.units[1], england.units[0], 'Belgium'),

        ConvoyMoveCommand(france, france.units[0], 'London'),
        ConvoyTransportCommand(france, france.units[1], france.units[0], 'London'),
    ]
    result = resolve_turn(game_map, commands)
    assert result == {
        'England' : {
            Unit(UnitTypes.TROOP, 'Belgium'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): None,
        },
        'France' : {
            Unit(UnitTypes.TROOP, 'London'): None,
            Unit(UnitTypes.FLEET, 'English Channel'): None,
        },
    }


def test_c_7__disrupted_unit_swap():
    """
    ENGLAND: A London -> Belgium (Convoy)
             F North Sea Transports London -> Belgium

    FRANCE:  A Belgium -> London (Convoy)
             F English Channel Transports Belgium -> London
             A Burgandy -> Belgium
    """
    game_map = generate_map()

    england_starting_configuration = [
        {'territory_name': 'London', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'North Sea', 'unit_type': UnitTypes.FLEET},
    ]
    england = Player("England", game_map, england_starting_configuration)

    france_starting_configuration = [
        {'territory_name': 'Belgium', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'English Channel', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Burgundy', 'unit_type': UnitTypes.TROOP},
    ]
    france = Player("France", game_map, france_starting_configuration)

    commands = [
        ConvoyMoveCommand(england, england.units[0], 'Belgium'),
        ConvoyTransportCommand(england, england.units[1], england.units[0], 'Belgium'),

        ConvoyMoveCommand(france, france.units[0], 'London'),
        ConvoyTransportCommand(france, france.units[1], france.units[0], 'London'),
        MoveCommand(france, france.units[2], 'Belgium'),
    ]
    result = resolve_turn(game_map, commands)
    assert result == {
        'England' : {
            Unit(UnitTypes.TROOP, 'London'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): None,
        },
        'France' : {
            Unit(UnitTypes.TROOP, 'Belgium'): None,
            Unit(UnitTypes.FLEET, 'English Channel'): None,
            Unit(UnitTypes.TROOP, 'Burgundy'): None,
        },
    }
