import pytest

from pydip.map.predefined.vanilla_dip import generate_map
from pydip.player.command.command import ConvoyTransportCommand
from pydip.player.player import Player
from pydip.player.unit import Unit, UnitTypes
from pydip.test.command_helper import CommandType, CommandHelper
from pydip.test.player_helper import PlayerHelper
from pydip.test.turn_helper import TurnHelper


def test_f_1__dislodged_unit_has_no_effect_on_attackers_area():
    """
    Adapted from DATC test, because the DATC test requires a fleet to be
    issued a convoy command from a coastal territory, which this system
    does not allow
    """
    game_map = generate_map()
    turkey_starting_configuration = [
        {'territory_name': 'Greece', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Constantinople Coast', 'unit_type': UnitTypes.FLEET},
    ]
    turkey = Player("Turkey", game_map, turkey_starting_configuration)

    with pytest.raises(AssertionError):
        ConvoyTransportCommand(turkey, turkey.units[1], turkey.units[0], 'Sevastopol')


def test_f_2__convoys_can_bounce_as_normal():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'London', 'Brest'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'London', 'Brest'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Paris', 'Brest'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'London'): None,
            Unit(UnitTypes.FLEET, 'English Channel'): None,
        },
        'France': {
            Unit(UnitTypes.TROOP, 'Paris'): None,
        },
    }


def test_f_3__an_army_being_convoyed_can_receive_support():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'London', 'Brest'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'London', 'Brest'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Mid-Atlantic Ocean', 'London', 'Brest'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Paris', 'Brest'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Brest'): None,
            Unit(UnitTypes.FLEET, 'English Channel'): None,
            Unit(UnitTypes.FLEET, 'Mid-Atlantic Ocean'): None,
        },
        'France': {
            Unit(UnitTypes.TROOP, 'Paris'): None,
        },
    }


def test_f_4__an_attacked_convoy_is_not_disrupted():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'London', 'Holland'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'North Sea', 'London', 'Holland'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Skagerrak', 'North Sea'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Holland'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): None,
        },
        'Germany': {
            Unit(UnitTypes.FLEET, 'Skagerrak'): None,
        },
    }


def test_f_5__a_beleaguered_convoy_is_not_disrupted():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'London', 'Holland'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'North Sea', 'London', 'Holland'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'English Channel', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Belgium Coast', 'English Channel', 'North Sea'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Skagerrak', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Denmark Coast', 'Skagerrak', 'North Sea'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Holland'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): None,
        },
        'France': {
            Unit(UnitTypes.FLEET, 'English Channel'): None,
            Unit(UnitTypes.FLEET, 'Belgium Coast'): None,
        },
        'Germany': {
            Unit(UnitTypes.FLEET, 'Skagerrak'): None,
            Unit(UnitTypes.FLEET, 'Denmark Coast'): None,
        },
    }


def test_f_6__dislodged_convoy_does_not_cut_support():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'London', 'Holland'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'North Sea', 'London', 'Holland'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Holland', 'Belgium', 'Belgium'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Belgium', 'Holland', 'Holland'),
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Skagerrak', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Helgoland Bight', 'Skagerrak', 'North Sea'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Picardy', 'Belgium'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Burgundy', 'Picardy', 'Belgium'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'London'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): {
                'Denmark Coast',
                'Norway Coast',
                'Norwegian Sea',
                'Edinburgh Coast',
                'Yorkshire Coast',
                'English Channel',
            },
        },
        'Germany': {
            Unit(UnitTypes.TROOP, 'Belgium'): None,
            Unit(UnitTypes.TROOP, 'Holland'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): None,
            Unit(UnitTypes.FLEET, 'Helgoland Bight'): None,
        },
        'France': {
            Unit(UnitTypes.TROOP, 'Picardy'): None,
            Unit(UnitTypes.TROOP, 'Burgundy'): None,
        },
    }


def test_f_7__dislodged_convoy_does_not_cause_contested_area():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'London', 'Holland'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'North Sea', 'London', 'Holland'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Skagerrak', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Helgoland Bight', 'Skagerrak', 'North Sea'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'London'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): {
                'Denmark Coast',
                'Norway Coast',
                'Norwegian Sea',
                'Edinburgh Coast',
                'Yorkshire Coast',
                'English Channel',
                'Belgium Coast',
                'Holland Coast',
            },
        },
        'Germany': {
            Unit(UnitTypes.FLEET, 'North Sea'): None,
            Unit(UnitTypes.FLEET, 'Helgoland Bight'): None,
        },
    }


def test_f_8__dislodged_convoy_does_not_cause_a_bounce():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'London', 'Holland'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'North Sea', 'London', 'Holland'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Skagerrak', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Helgoland Bight', 'Skagerrak', 'North Sea'),
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Belgium', 'Holland'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'London'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): {
                'Denmark Coast',
                'Norway Coast',
                'Norwegian Sea',
                'Edinburgh Coast',
                'Yorkshire Coast',
                'English Channel',
                'Belgium Coast',
            },
        },
        'Germany': {
            Unit(UnitTypes.FLEET, 'North Sea'): None,
            Unit(UnitTypes.FLEET, 'Helgoland Bight'): None,
            Unit(UnitTypes.TROOP, 'Holland'): None,
        },
    }


def test_f_9__dislodge_of_multi_route_convoy():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'London', 'Belgium'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'North Sea', 'London', 'Belgium'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'London', 'Belgium'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Mid-Atlantic Ocean', 'English Channel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Brest Coast', 'Mid-Atlantic Ocean', 'English Channel'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Belgium'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): None,
            Unit(UnitTypes.FLEET, 'English Channel'): {
                'London Coast',
                'Irish Sea',
                'Wales Coast',
                'Picardy Coast',
            },
        },
        'France': {
            Unit(UnitTypes.FLEET, 'English Channel'): None,
            Unit(UnitTypes.FLEET, 'Brest Coast'): None,
        },
    }


def test_f_10__dislodge_of_multi_route_convoy_with_foreign_fleet():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'London', 'Belgium'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'North Sea', 'London', 'Belgium'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'London', 'Belgium'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Mid-Atlantic Ocean', 'English Channel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Brest Coast', 'Mid-Atlantic Ocean', 'English Channel'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Belgium'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): None,
        },
        'Germany': {
            Unit(UnitTypes.FLEET, 'English Channel'): {
                'London Coast',
                'Irish Sea',
                'Wales Coast',
                'Picardy Coast',
            },
        },
        'France': {
            Unit(UnitTypes.FLEET, 'English Channel'): None,
            Unit(UnitTypes.FLEET, 'Brest Coast'): None,
        },
    }


def test_f_11__dislodge_of_multi_route_convoy_with_only_foreign_fleets():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'London', 'Belgium'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'North Sea', 'London', 'Belgium'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'London', 'Belgium'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Mid-Atlantic Ocean', 'English Channel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Brest Coast', 'Mid-Atlantic Ocean', 'English Channel'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Belgium'): None,
        },
        'Russia': {
            Unit(UnitTypes.FLEET, 'North Sea'): None,
        },
        'Germany': {
            Unit(UnitTypes.FLEET, 'English Channel'): {
                'London Coast',
                'Irish Sea',
                'Wales Coast',
                'Picardy Coast',
            },
        },
        'France': {
            Unit(UnitTypes.FLEET, 'English Channel'): None,
            Unit(UnitTypes.FLEET, 'Brest Coast'): None,
        },
    }


def test_f_12__dislodged_convoying_fleet_not_on_route():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'London', 'Belgium'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'North Sea', 'London', 'Belgium'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Irish Sea', 'London', 'Belgium'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Mid-Atlantic Ocean', 'Irish Sea'),
            CommandHelper(
                CommandType.SUPPORT,
                UnitTypes.FLEET,
                'North Atlantic Ocean',
                'Mid-Atlantic Ocean',
                'Irish Sea',
            ),
        ])
    ])
    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Belgium'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): None,
            Unit(UnitTypes.FLEET, 'Irish Sea'): {
                'Liverpool Coast',
                'Wales Coast',
                'English Channel',
            },
        },
        'France': {
            Unit(UnitTypes.FLEET, 'Irish Sea'): None,
            Unit(UnitTypes.FLEET, 'North Atlantic Ocean'): None,
        },
    }


def test_f_13__the_unwanted_alternative():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'London', 'Belgium'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'North Sea', 'London', 'Belgium'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'London', 'Belgium'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Denmark Coast', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Holland Coast', 'Denmark Coast', 'North Sea'),
        ])
    ])
    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Belgium'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): {
                'Skagerrak',
                'Helgoland Bight',
                'London Coast',
                'Yorkshire Coast',
                'Edinburgh Coast',
                'Norwegian Sea',
                'Norway Coast',
            },
        },
        'France': {
            Unit(UnitTypes.FLEET, 'English Channel'): None,
        },
        'Germany': {
            Unit(UnitTypes.FLEET, 'North Sea'): None,
            Unit(UnitTypes.FLEET, 'Holland Coast'): None,
        },
    }


def test_f_14__simple_convoy_paradox():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Wales Coast', 'English Channel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'London Coast', 'Wales Coast', 'English Channel'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Brest', 'London'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'Brest', 'London'),
        ])
    ])
    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.FLEET, 'London Coast'): None,
            Unit(UnitTypes.FLEET, 'English Channel'): None,
        },
        'France': {
            Unit(UnitTypes.TROOP, 'Brest'): None,
            Unit(UnitTypes.FLEET, 'English Channel'): {
                'Irish Sea',
                'Mid-Atlantic Ocean',
                'North Sea',
                'Belgium Coast',
                'Picardy Coast',
            },
        },
    }


def test_f_15__simple_convoy_paradox_with_additional_convoy():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Wales Coast', 'English Channel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'London Coast', 'Wales Coast', 'English Channel'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Brest', 'London'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'Brest', 'London'),
        ]),
        PlayerHelper('Italy', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'North Africa', 'Wales'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Mid-Atlantic Ocean', 'North Africa', 'Wales'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Irish Sea', 'North Africa', 'Wales'),
        ])
    ])
    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.FLEET, 'London Coast'): None,
            Unit(UnitTypes.FLEET, 'English Channel'): None,
        },
        'France': {
            Unit(UnitTypes.TROOP, 'Brest'): None,
            Unit(UnitTypes.FLEET, 'English Channel'): {
                'North Sea',
                'Belgium Coast',
                'Picardy Coast',
            },
        },
        'Italy': {
            Unit(UnitTypes.TROOP, 'Wales'): None,
            Unit(UnitTypes.FLEET, 'Mid-Atlantic Ocean'): None,
            Unit(UnitTypes.FLEET, 'Irish Sea'): None,
        },
    }


def test_f_16__pandins_paradox():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Wales Coast', 'English Channel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'London Coast', 'Wales Coast', 'English Channel'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Brest', 'London'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'Brest', 'London'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Belgium Coast', 'English Channel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'North Sea', 'Belgium Coast', 'English Channel'),
        ])
    ])
    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.FLEET, 'London Coast'): None,
            Unit(UnitTypes.FLEET, 'Wales Coast'): None,
        },
        'France': {
            Unit(UnitTypes.TROOP, 'Brest'): None,
            Unit(UnitTypes.FLEET, 'English Channel'): None,
        },
        'Germany': {
            Unit(UnitTypes.FLEET, 'Belgium Coast'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): None,
        },
    }


def test_f_17__pandins_extended_paradox():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Wales Coast', 'English Channel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'London Coast', 'Wales Coast', 'English Channel'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Brest', 'London'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'Brest', 'London'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Yorkshire Coast', 'Brest', 'London'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Belgium Coast', 'English Channel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'North Sea', 'Belgium Coast', 'English Channel'),
        ])
    ])
    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.FLEET, 'London Coast'): None,
            Unit(UnitTypes.FLEET, 'Wales Coast'): None,
        },
        'France': {
            Unit(UnitTypes.TROOP, 'Brest'): None,
            Unit(UnitTypes.FLEET, 'English Channel'): None,
            Unit(UnitTypes.FLEET, 'Yorkshire Coast'): None,
        },
        'Germany': {
            Unit(UnitTypes.FLEET, 'Belgium Coast'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): None,
        },
    }


def test_f_18__betrayal_paradox():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'London', 'Belgium'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'North Sea', 'London', 'Belgium'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'English Channel', 'London', 'Belgium'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Belgium Coast', 'North Sea', 'North Sea'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Skagerrak', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Helgoland Bight', 'Skagerrak', 'North Sea'),
        ])
    ])
    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'London'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): None,
            Unit(UnitTypes.FLEET, 'English Channel'): None,
        },
        'France': {
            Unit(UnitTypes.FLEET, 'Belgium Coast'): None,
        },
        'Germany': {
            Unit(UnitTypes.FLEET, 'Skagerrak'): None,
            Unit(UnitTypes.FLEET, 'Helgoland Bight'): None,
        },
    }


def test_f_19__multi_route_convoy_disruption_paradox():
    helper = TurnHelper([
        PlayerHelper('France', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Tunis', 'Naples'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Tyrrhenian Sea', 'Tunis', 'Naples'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Ionian Sea', 'Tunis', 'Naples'),
        ]),
        PlayerHelper('Italy', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Rome Coast', 'Tyrrhenian Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Naples Coast', 'Rome Coast', 'Tyrrhenian Sea'),
        ])
    ])
    result = helper.resolve()
    assert result == {
        'France': {
            Unit(UnitTypes.TROOP, 'Tunis'): None,
            Unit(UnitTypes.FLEET, 'Tyrrhenian Sea'): None,
            Unit(UnitTypes.FLEET, 'Ionian Sea'): None,
        },
        'Italy': {
            Unit(UnitTypes.FLEET, 'Naples Coast'): None,
            Unit(UnitTypes.FLEET, 'Rome Coast'): None,
        },
    }


def test_f_20__unwanted_multi_route_convoy_paradox():
    helper = TurnHelper([
        PlayerHelper('France', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Tunis', 'Naples'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Tyrrhenian Sea', 'Tunis', 'Naples'),
        ]),
        PlayerHelper('Italy', [
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Ionian Sea', 'Tunis', 'Naples'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Naples Coast', 'Ionian Sea', 'Ionian Sea'),
        ]),
        PlayerHelper('Turkey', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Eastern Mediterranean Sea', 'Ionian Sea'),
            CommandHelper(
                CommandType.SUPPORT,
                UnitTypes.FLEET,
                'Aegean Sea',
                'Eastern Mediterranean Sea',
                'Ionian Sea'
            ),
        ])
    ])
    result = helper.resolve()
    assert result == {
        'France': {
            Unit(UnitTypes.TROOP, 'Tunis'): None,
            Unit(UnitTypes.FLEET, 'Tyrrhenian Sea'): None,
        },
        'Italy': {
            Unit(UnitTypes.FLEET, 'Naples Coast'): None,
            Unit(UnitTypes.FLEET, 'Ionian Sea'): {
                'Greece Coast',
                'Albania Coast',
                'Adriatic Sea',
                'Apulia Coast',
            },
        },
        'Turkey': {
            Unit(UnitTypes.FLEET, 'Ionian Sea'): None,
            Unit(UnitTypes.FLEET, 'Aegean Sea'): None,
        },
    }


def test_f_21__dads_army_convoy():
    helper = TurnHelper([
        PlayerHelper('Russia', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Norway', 'Clyde'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Norwegian Sea', 'Norway', 'Clyde'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Edinburgh', 'Norway', 'Clyde'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Mid-Atlantic Ocean', 'North Atlantic Ocean'),
            CommandHelper(
                CommandType.SUPPORT,
                UnitTypes.FLEET,
                'Irish Sea',
                'Mid-Atlantic Ocean',
                'North Atlantic Ocean',
            ),
        ]),
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Liverpool', 'Clyde'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'North Atlantic Ocean', 'Liverpool', 'Clyde'),
            CommandHelper(
                CommandType.SUPPORT,
                UnitTypes.FLEET,
                'Clyde Coast',
                'North Atlantic Ocean',
                'North Atlantic Ocean',
            ),
        ])
    ])
    result = helper.resolve()
    assert result == {
        'Russia': {
            Unit(UnitTypes.TROOP, 'Clyde'): None,
            Unit(UnitTypes.FLEET, 'Norwegian Sea'): None,
            Unit(UnitTypes.TROOP, 'Edinburgh'): None,
        },
        'France': {
            Unit(UnitTypes.FLEET, 'North Atlantic Ocean'): None,
            Unit(UnitTypes.FLEET, 'Irish Sea'): None,
        },
        'England': {
            Unit(UnitTypes.TROOP, 'Liverpool'): None,
            Unit(UnitTypes.FLEET, 'North Atlantic Ocean'): set(),
            Unit(UnitTypes.FLEET, 'Clyde Coast'): set(),
        },
    }


def test_f_22__second_order_paradox_with_two_resolutions():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Edinburgh Coast', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'London Coast', 'Edinburgh Coast', 'North Sea'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Brest', 'London'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'Brest', 'London'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Picardy Coast', 'English Channel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Belgium Coast', 'Picardy Coast', 'English Channel'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Norway', 'Belgium'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'North Sea', 'Norway', 'Belgium'),
        ])
    ])
    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.FLEET, 'North Sea'): None,
            Unit(UnitTypes.FLEET, 'London Coast'): None,
        },
        'France': {
            Unit(UnitTypes.TROOP, 'Brest'): None,
            Unit(UnitTypes.FLEET, 'English Channel'): {
                'Mid-Atlantic Ocean',
                'Irish Sea',
                'Wales Coast',
            },
        },
        'Germany': {
            Unit(UnitTypes.FLEET, 'English Channel'): None,
            Unit(UnitTypes.FLEET, 'Belgium Coast'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Norway'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): {
                'Yorkshire Coast',
                'Norwegian Sea',
                'Skagerrak',
                'Denmark Coast',
                'Helgoland Bight',
                'Holland Coast',
            },
        },
    }


def test_f_23__second_order_paradox_with_two_exclusive_convoys():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Edinburgh Coast', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Yorkshire Coast', 'Edinburgh Coast', 'North Sea'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Brest', 'London'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'Brest', 'London'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Belgium Coast', 'English Channel', 'English Channel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'London Coast', 'North Sea', 'North Sea'),
        ]),
        PlayerHelper('Italy', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Mid-Atlantic Ocean', 'English Channel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Irish Sea', 'Mid-Atlantic Ocean', 'English Channel'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Norway', 'Belgium'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'North Sea', 'Norway', 'Belgium'),
        ])
    ])
    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.FLEET, 'Edinburgh Coast'): None,
            Unit(UnitTypes.FLEET, 'Yorkshire Coast'): None,
        },
        'France': {
            Unit(UnitTypes.TROOP, 'Brest'): None,
            Unit(UnitTypes.FLEET, 'English Channel'): None,
        },
        'Germany': {
            Unit(UnitTypes.FLEET, 'London Coast'): None,
            Unit(UnitTypes.FLEET, 'Belgium Coast'): None,
        },
        'Italy': {
            Unit(UnitTypes.FLEET, 'Mid-Atlantic Ocean'): None,
            Unit(UnitTypes.FLEET, 'Irish Sea'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Norway'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): None,
        },
    }


def test_f_24__second_order_paradox_with_no_resolution():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Edinburgh Coast', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'London Coast', 'Edinburgh Coast', 'North Sea'),
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Irish Sea', 'English Channel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Mid-Atlantic Ocean', 'Irish Sea', 'English Channel'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Brest', 'London'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'Brest', 'London'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Belgium Coast', 'English Channel', 'English Channel')
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Norway', 'Belgium'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'North Sea', 'Norway', 'Belgium'),
        ])
    ])
    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.FLEET, 'North Sea'): None,
            Unit(UnitTypes.FLEET, 'London Coast'): None,
            Unit(UnitTypes.FLEET, 'Irish Sea'): None,
            Unit(UnitTypes.FLEET, 'Mid-Atlantic Ocean'): None,
        },
        'France': {
            Unit(UnitTypes.TROOP, 'Brest'): None,
            Unit(UnitTypes.FLEET, 'English Channel'): None,
            Unit(UnitTypes.FLEET, 'Belgium Coast'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Norway'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): {
                'Norwegian Sea',
                'Skagerrak',
                'Helgoland Bight',
                'Denmark Coast',
                'Holland Coast',
                'Yorkshire Coast',
            },
        },
    }
