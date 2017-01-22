import pytest

from pydip.player.unit import Unit, UnitTypes
from pydip.test.command_helper import RetreatCommandHelper, RetreatCommandType, CommandHelper, CommandType
from pydip.test.player_helper import PlayerHelper
from pydip.test.retreat_helper import RetreatHelper


# Tests H.1-H.3 have been skipped, because they deal with players
# issuing non-retreat commands during the retreat step, which this
# system does not permit.

# Test H.4 has been modified, since it relates to a user issuing a
# command to a non-retreating unit during the retreat step. This is
# not allowed by the system, so this test simply asserts that fact.
from pydip.test.turn_helper import TurnHelper


def test_h_4__no_other_moves_during_retreat():
    retreat_map = {
        'England': {
            Unit(UnitTypes.TROOP, 'Holland'): {
                'Belgium',
            },
            Unit(UnitTypes.FLEET, 'North Sea'): None,
        },
        'Germany': {
            Unit(UnitTypes.TROOP, 'Holland'): None,
            Unit(UnitTypes.FLEET, 'Kiel Coast'): None,
        }
    }
    with pytest.raises(AssertionError):
        RetreatHelper(
            retreat_map,
            [
                PlayerHelper('England', [
                    RetreatCommandHelper(RetreatCommandType.MOVE, retreat_map, UnitTypes.TROOP, 'Holland', 'Belgium'),
                    RetreatCommandHelper(
                        RetreatCommandType.MOVE,
                        retreat_map,
                        UnitTypes.FLEET,
                        'North Sea',
                        'Norwegian Sea',
                    ),
                ]),
            ]
        )


def test_h_5__a_unit_may_not_retreat_to_the_area_from_which_it_is_attacked():
    helper = TurnHelper([
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Black Sea', 'Ankara Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Constantinople Coast', 'Black Sea', 'Ankara Coast'),
        ]),
        PlayerHelper('Turkey', [
            CommandHelper(CommandType.HOLD, UnitTypes.FLEET, 'Ankara Coast'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'Russia': {
            Unit(UnitTypes.FLEET, 'Ankara Coast'): None,
            Unit(UnitTypes.FLEET, 'Constantinople Coast'): None,
        },
        'Turkey': {
            Unit(UnitTypes.FLEET, 'Ankara Coast'): {
                'Armenia Coast',
            },
        },
    }


def test_h_6__unit_may_not_retreat_to_a_contested_area():
    helper = TurnHelper([
        PlayerHelper('Austria', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Trieste', 'Vienna'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Budapest', 'Trieste', 'Vienna'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Munich', 'Bohemia'),
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Silesia', 'Bohemia'),
        ]),
        PlayerHelper('Italy', [
            CommandHelper(CommandType.HOLD, UnitTypes.TROOP, 'Vienna'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'Austria': {
            Unit(UnitTypes.TROOP, 'Vienna'): None,
            Unit(UnitTypes.TROOP, 'Budapest'): None,
        },
        'Germany': {
            Unit(UnitTypes.TROOP, 'Munich'): None,
            Unit(UnitTypes.TROOP, 'Silesia'): None,
        },
        'Italy': {
            Unit(UnitTypes.TROOP, 'Vienna'): {
                'Tyrolia',
                'Galicia',
            },
        },
    }


def test_h_7__multiple_retreat_to_same_area_will_disband_units():
    retreat_map = {
        'Austria': {
            Unit(UnitTypes.TROOP, 'Budapest'): None,
            Unit(UnitTypes.TROOP, 'Vienna'): None,
        },
        'Germany': {
            Unit(UnitTypes.TROOP, 'Bohemia'): None,
            Unit(UnitTypes.TROOP, 'Munich'): None,
        },
        'Italy': {
            Unit(UnitTypes.TROOP, 'Vienna'): {
                'Galicia',
                'Tyrolia',
            },
            Unit(UnitTypes.TROOP, 'Bohemia'): {
                'Galicia',
                'Tyrolia',
            },
        },
    }
    helper = RetreatHelper(
        retreat_map,
        [
            PlayerHelper('Italy', [
                RetreatCommandHelper(RetreatCommandType.MOVE, retreat_map, UnitTypes.TROOP, 'Vienna', 'Tyrolia'),
                RetreatCommandHelper(RetreatCommandType.MOVE, retreat_map, UnitTypes.TROOP, 'Bohemia', 'Tyrolia'),
            ]),
        ]
    )

    result = helper.resolve()
    assert result == {
        'Austria' : { Unit(UnitTypes.TROOP, 'Budapest'), Unit(UnitTypes.TROOP, 'Vienna') },
        'Germany' : { Unit(UnitTypes.TROOP, 'Bohemia'), Unit(UnitTypes.TROOP, 'Munich') },
        'Italy' : set(),
    }


def test_h_8__triple_retreat_to_same_area_will_disband_units():
    retreat_map = {
        'England': {
            Unit(UnitTypes.TROOP, 'Edinburgh'): None,
            Unit(UnitTypes.FLEET, 'Yorkshire Coast'): None,
            Unit(UnitTypes.FLEET, 'Norway Coast'): {
                'North Sea',
                'Norwegian Sea',
                'Skagerrak',
            },
        },
        'Germany': {
            Unit(UnitTypes.TROOP, 'Holland'): None,
            Unit(UnitTypes.TROOP, 'Kiel'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Norway'): None,
            Unit(UnitTypes.TROOP, 'Sweden'): None,
            Unit(UnitTypes.FLEET, 'Edinburgh Coast'): {
                'Clyde Coast',
                'North Sea',
                'Norwegian Sea',
            },
            Unit(UnitTypes.FLEET, 'Holland Coast'): {
                'North Sea',
                'Helgoland Bight',
                'Belgium Coast',
            },
        },
    }
    helper = RetreatHelper(
        retreat_map,
        [
            PlayerHelper('England', [
                RetreatCommandHelper(
                    RetreatCommandType.MOVE,
                    retreat_map,
                    UnitTypes.FLEET,
                    'Norway Coast',
                    'North Sea',
                ),
            ]),
            PlayerHelper('Russia', [
                RetreatCommandHelper(
                    RetreatCommandType.MOVE,
                    retreat_map,
                    UnitTypes.FLEET,
                    'Edinburgh Coast',
                    'North Sea',
                ),
                RetreatCommandHelper(
                    RetreatCommandType.MOVE,
                    retreat_map,
                    UnitTypes.FLEET,
                    'Holland Coast',
                    'North Sea',
                ),
            ]),
        ]
    )

    result = helper.resolve()
    assert result == {
        'England' : { Unit(UnitTypes.TROOP, 'Edinburgh'), Unit(UnitTypes.FLEET, 'Yorkshire Coast') },
        'Germany' : { Unit(UnitTypes.TROOP, 'Holland'), Unit(UnitTypes.TROOP, 'Kiel') },
        'Russia'  : { Unit(UnitTypes.TROOP, 'Norway'), Unit(UnitTypes.TROOP, 'Sweden') },
    }


def test_h_9__dislodged_unit_will_not_make_attackers_area_contested():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Helgoland Bight', 'Kiel Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Denmark Coast', 'Helgoland Bight', 'Kiel Coast'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Berlin', 'Prussia'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Silesia', 'Berlin', 'Prussia'),
            CommandHelper(CommandType.HOLD, UnitTypes.FLEET, 'Kiel Coast'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Prussia', 'Berlin'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.FLEET, 'Kiel Coast'): None,
            Unit(UnitTypes.FLEET, 'Denmark Coast'): None,
        },
        'Germany': {
            Unit(UnitTypes.TROOP, 'Prussia'): None,
            Unit(UnitTypes.TROOP, 'Silesia'): None,
            Unit(UnitTypes.FLEET, 'Kiel Coast'): {
                'Baltic Sea',
                'Berlin Coast',
                'Holland Coast',
            },
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Prussia'): {
                'Livonia',
                'Warsaw',
            },
        },
    }


def test_h_10__not_retreating_to_attacker_does_not_mean_contested():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.HOLD, UnitTypes.TROOP, 'Kiel'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Berlin', 'Kiel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Munich', 'Berlin', 'Kiel'),
            CommandHelper(CommandType.HOLD, UnitTypes.TROOP, 'Prussia'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Warsaw', 'Prussia'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Silesia', 'Warsaw', 'Prussia'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Kiel'): {
                'Ruhr',
                'Holland',
                'Denmark',
            },
        },
        'Germany': {
            Unit(UnitTypes.TROOP, 'Kiel'): None,
            Unit(UnitTypes.TROOP, 'Munich'): None,
            Unit(UnitTypes.TROOP, 'Prussia'): {
                'Livonia',
                'Berlin',
            },
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Prussia'): None,
            Unit(UnitTypes.TROOP, 'Silesia'): None,
        },
    }


def test_h_11__retreat_when_dislodged_by_adjacent_convoy():
    helper = TurnHelper([
        PlayerHelper('France', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Gascony', 'Marseilles'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Mid-Atlantic Ocean', 'Gascony', 'Marseilles'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Gulf of Lyon', 'Gascony', 'Marseilles'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Burgundy', 'Gascony', 'Marseilles'),
            CommandHelper(
                CommandType.CONVOY_TRANSPORT,
                UnitTypes.FLEET,
                'Western Mediterranean Sea',
                'Gascony',
                'Marseilles',
            ),
        ]),
        PlayerHelper('Italy', [
            CommandHelper(CommandType.HOLD, UnitTypes.TROOP, 'Marseilles'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'France': {
            Unit(UnitTypes.TROOP, 'Marseilles'): None,
            Unit(UnitTypes.FLEET, 'Mid-Atlantic Ocean'): None,
            Unit(UnitTypes.FLEET, 'Western Mediterranean Sea'): None,
            Unit(UnitTypes.FLEET, 'Gulf of Lyon'): None,
            Unit(UnitTypes.TROOP, 'Burgundy'): None,
        },
        'Italy': {
            Unit(UnitTypes.TROOP, 'Marseilles'): {
                'Piedmont',
                'Gascony',
                'Spain',
            },
        },
    }


def test_h_12__retreat_when_dislodged_by_adjacent_convoy_while_trying_to_do_the_same():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Liverpool', 'Edinburgh'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'Liverpool', 'Edinburgh'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Irish Sea', 'Liverpool', 'Edinburgh'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'North Sea', 'Liverpool', 'Edinburgh'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Brest Coast', 'English Channel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Mid-Atlantic Ocean', 'Brest Coast', 'English Channel'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Edinburgh', 'Liverpool'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Norwegian Sea', 'Edinburgh', 'Liverpool'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Clyde', 'Edinburgh', 'Liverpool'),
            CommandHelper(
                CommandType.CONVOY_TRANSPORT,
                UnitTypes.FLEET,
                'North Atlantic Ocean',
                'Edinburgh',
                'Liverpool',
            ),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Liverpool'): {
                'Edinburgh',
                'Yorkshire',
                'Wales',
            },
            Unit(UnitTypes.FLEET, 'English Channel'): {
                'London Coast',
                'Wales Coast',
                'Picardy Coast',
                'Belgium Coast',
            },
            Unit(UnitTypes.FLEET, 'Irish Sea'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): None,
        },
        'France': {
            Unit(UnitTypes.FLEET, 'English Channel'): None,
            Unit(UnitTypes.FLEET, 'Mid-Atlantic Ocean'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Liverpool'): None,
            Unit(UnitTypes.FLEET, 'Norwegian Sea'): None,
            Unit(UnitTypes.FLEET, 'North Atlantic Ocean'): None,
            Unit(UnitTypes.TROOP, 'Clyde'): None,
        },
    }


def test_h_13__no_retreat_with_convoy_in_main_phase():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.HOLD, UnitTypes.TROOP, 'Picardy'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'Picardy', 'London'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Paris', 'Picardy'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Brest', 'Paris', 'Picardy'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Picardy'): {
                'Belgium',
                'Burgundy',
            },
            Unit(UnitTypes.FLEET, 'English Channel'): None,
        },
        'France': {
            Unit(UnitTypes.TROOP, 'Picardy'): None,
            Unit(UnitTypes.TROOP, 'Brest'): None,
        },
    }


# Test H.14 is skipped, because it is about ensuring context from the main
# phase does not leak to the retreat phase. That notion is incompatible with
# this system, and makes the test superfluous and verbose


def test_h_15__no_coastal_crawl_in_retreat():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.HOLD, UnitTypes.FLEET, 'Portugal Coast'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Spain South Coast', 'Portugal Coast'),
            CommandHelper(
                CommandType.SUPPORT,
                UnitTypes.FLEET,
                'Mid-Atlantic Ocean',
                'Spain South Coast',
                'Portugal Coast',
            ),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.FLEET, 'Portugal Coast'): set(),
        },
        'France': {
            Unit(UnitTypes.FLEET, 'Portugal Coast'): None,
            Unit(UnitTypes.FLEET, 'Mid-Atlantic Ocean'): None,
        },
    }


def test_h_16__contested_for_both_coasts():
    helper = TurnHelper([
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Mid-Atlantic Ocean', 'Spain North Coast'),
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Gascony Coast', 'Spain North Coast'),
            CommandHelper(CommandType.HOLD, UnitTypes.FLEET, 'Western Mediterranean Sea'),
        ]),
        PlayerHelper('Italy', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Tyrrhenian Sea', 'Western Mediterranean Sea'),
            CommandHelper(
                CommandType.SUPPORT,
                UnitTypes.FLEET,
                'Tunis Coast',
                'Tyrrhenian Sea',
                'Western Mediterranean Sea',
            ),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'France': {
            Unit(UnitTypes.FLEET, 'Mid-Atlantic Ocean'): None,
            Unit(UnitTypes.FLEET, 'Gascony Coast'): None,
            Unit(UnitTypes.FLEET, 'Western Mediterranean Sea'): {
                'North Africa Coast',
                'Gulf of Lyon',
            },
        },
        'Italy': {
            Unit(UnitTypes.FLEET, 'Western Mediterranean Sea'): None,
            Unit(UnitTypes.FLEET, 'Tunis Coast'): None,
        },
    }
