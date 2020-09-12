from pydip.player.unit import Unit, UnitTypes
from pydip.test.command_helper import CommandType, CommandHelper
from pydip.test.player_helper import PlayerHelper
from pydip.test.turn_helper import TurnHelper


def test_g_1__two_units_can_swap_places_by_convoy():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Norway', 'Sweden'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Skagerrak', 'Norway', 'Sweden'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Sweden', 'Norway'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Sweden'): None,
            Unit(UnitTypes.FLEET, 'Skagerrak'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Norway'): None,
        },
    }


# Tests G.2-G.4, G.9, and G.11 have been modified, because they rely on ambiguous convoy /
# movements, which this system does not allow. Each test has been duplicated to test each
# potential interpretation is covered appropriately by the system, just for thorough testing.


def test_g_2a__kidnapping_an_army():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Norway', 'Sweden'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Sweden', 'Norway'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Skagerrak', 'Norway', 'Sweden'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Norway'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Sweden'): None,
        },
        'Germany': {
            Unit(UnitTypes.FLEET, 'Skagerrak'): None,
        },
    }


def test_g_2b__kidnapping_an_army():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Norway', 'Sweden'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Sweden', 'Norway'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Skagerrak', 'Norway', 'Sweden'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Sweden'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Norway'): None,
        },
        'Germany': {
            Unit(UnitTypes.FLEET, 'Skagerrak'): None,
        },
    }


def test_g_3a__kidnapping_with_a_disrupted_convoy():
    helper = TurnHelper([
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Brest Coast', 'English Channel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Mid-Atlantic Ocean', 'Brest Coast', 'English Channel'),
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Picardy', 'Belgium'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Burgundy', 'Picardy', 'Belgium'),
        ]),
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'Picardy', 'Belgium'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'France': {
            Unit(UnitTypes.FLEET, 'English Channel'): None,
            Unit(UnitTypes.FLEET, 'Mid-Atlantic Ocean'): None,
            Unit(UnitTypes.TROOP, 'Belgium'): None,
            Unit(UnitTypes.TROOP, 'Burgundy'): None,
        },
        'England': {
            Unit(UnitTypes.FLEET, 'English Channel'): {
                'Irish Sea',
                'Wales Coast',
                'London Coast',
                'North Sea',
                'Picardy Coast',
            },
        },
    }


def test_g_3b__kidnapping_with_a_disrupted_convoy():
    helper = TurnHelper([
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Brest Coast', 'English Channel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Mid-Atlantic Ocean', 'Brest Coast', 'English Channel'),
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Picardy', 'Belgium'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Burgundy', 'Picardy', 'Belgium'),
        ]),
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'Picardy', 'Belgium'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'France': {
            Unit(UnitTypes.FLEET, 'English Channel'): None,
            Unit(UnitTypes.FLEET, 'Mid-Atlantic Ocean'): None,
            Unit(UnitTypes.TROOP, 'Picardy'): None,
            Unit(UnitTypes.TROOP, 'Burgundy'): None,
        },
        'England': {
            Unit(UnitTypes.FLEET, 'English Channel'): {
                'Belgium Coast',
                'Irish Sea',
                'Wales Coast',
                'London Coast',
                'North Sea',
            },
        },
    }


def test_g_4a__kidnapping_with_a_disrupted_convoy_and_opposite_move():
    helper = TurnHelper([
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Brest Coast', 'English Channel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Mid-Atlantic Ocean', 'Brest Coast', 'English Channel'),
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Picardy', 'Belgium'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Burgundy', 'Picardy', 'Belgium'),
        ]),
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'Picardy', 'Belgium'),
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Belgium', 'Picardy'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'France': {
            Unit(UnitTypes.FLEET, 'English Channel'): None,
            Unit(UnitTypes.FLEET, 'Mid-Atlantic Ocean'): None,
            Unit(UnitTypes.TROOP, 'Belgium'): None,
            Unit(UnitTypes.TROOP, 'Burgundy'): None,
        },
        'England': {
            Unit(UnitTypes.FLEET, 'English Channel'): {
                'Picardy Coast',
                'Irish Sea',
                'Wales Coast',
                'London Coast',
                'North Sea',
            },
            Unit(UnitTypes.TROOP, 'Belgium'): {
                'Holland',
                'Ruhr',
            },
        },
    }


def test_g_4b__kidnapping_with_a_disrupted_convoy_and_opposite_move():
    helper = TurnHelper([
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Brest Coast', 'English Channel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Mid-Atlantic Ocean', 'Brest Coast', 'English Channel'),
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Picardy', 'Belgium'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Burgundy', 'Picardy', 'Belgium'),
        ]),
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'Picardy', 'Belgium'),
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Belgium', 'Picardy'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'France': {
            Unit(UnitTypes.FLEET, 'English Channel'): None,
            Unit(UnitTypes.FLEET, 'Mid-Atlantic Ocean'): None,
            Unit(UnitTypes.TROOP, 'Picardy'): None,
            Unit(UnitTypes.TROOP, 'Burgundy'): None,
        },
        'England': {
            Unit(UnitTypes.FLEET, 'English Channel'): {
                'Irish Sea',
                'Wales Coast',
                'London Coast',
                'North Sea',
            },
            Unit(UnitTypes.TROOP, 'Belgium'): None,
        },
    }


# Tests G.5-G.7 are excluded, because they are based on the notion of using "intent"
# to determine whether a convoy or a move order was intended, which is not permitted
# in this system. The tests are not meaningful, so are skipped.


def test_g_8__explicit_convoy_that_is_not_there():
    helper = TurnHelper([
        PlayerHelper('France', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Belgium', 'Holland'),
        ]),
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'North Sea', 'Helgoland Bight'),
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Holland', 'Kiel'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'France': {
            Unit(UnitTypes.TROOP, 'Belgium'): None,
        },
        'England': {
            Unit(UnitTypes.FLEET, 'Helgoland Bight'): None,
            Unit(UnitTypes.TROOP, 'Kiel'): None,
        },
    }


def test_g_9a__swapped_or_dislodged():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Norway', 'Sweden'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Skagerrak', 'Norway', 'Sweden'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Finland Coast', 'Norway', 'Sweden'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Sweden', 'Norway'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Sweden'): None,
            Unit(UnitTypes.FLEET, 'Skagerrak'): None,
            Unit(UnitTypes.FLEET, 'Finland Coast'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Sweden'): {
                'Denmark',
            },
        },
    }


def test_g_9b__swapped_or_dislodged():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Norway', 'Sweden'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Skagerrak', 'Norway', 'Sweden'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Finland Coast', 'Norway', 'Sweden'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Sweden', 'Norway'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Sweden'): None,
            Unit(UnitTypes.FLEET, 'Skagerrak'): None,
            Unit(UnitTypes.FLEET, 'Finland Coast'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Norway'): None,
        },
    }


def test_g_10__swapped_or_head_to_head_battle():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Norway', 'Sweden'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Denmark Coast', 'Norway', 'Sweden'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Finland Coast', 'Norway', 'Sweden'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Skagerrak', 'Norway', 'Sweden'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Sweden', 'Norway'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Barents Sea', 'Sweden', 'Norway'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Norwegian Sea', 'Norway Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'North Sea', 'Norwegian Sea', 'Norway Coast'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Sweden'): None,
            Unit(UnitTypes.FLEET, 'Denmark Coast'): None,
            Unit(UnitTypes.FLEET, 'Finland Coast'): None,
        },
        'Germany': {
            Unit(UnitTypes.FLEET, 'Skagerrak'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Sweden'): set(),
            Unit(UnitTypes.FLEET, 'Barents Sea'): None,
        },
        'France': {
            Unit(UnitTypes.FLEET, 'Norwegian Sea'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): None,
        },
    }


def test_g_11a__a_convoy_to_an_adjacent_place_with_a_paradox():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'North Sea', 'Skagerrak'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Norway Coast', 'North Sea', 'Skagerrak'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Sweden', 'Norway'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Skagerrak', 'Sweden', 'Norway'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Barents Sea', 'Sweden', 'Norway'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.FLEET, 'North Sea'): None,
            Unit(UnitTypes.FLEET, 'Norway Coast'): {
                'Norwegian Sea',
                'St. Petersburg North Coast',
            },
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Norway'): None,
            Unit(UnitTypes.FLEET, 'Skagerrak'): None,
            Unit(UnitTypes.FLEET, 'Barents Sea'): None,
        },
    }


def test_g_11b__a_convoy_to_an_adjacent_place_with_a_paradox():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'North Sea', 'Skagerrak'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Norway Coast', 'North Sea', 'Skagerrak'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Sweden', 'Norway'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Skagerrak', 'Sweden', 'Norway'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Barents Sea', 'Sweden', 'Norway'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.FLEET, 'Norway Coast'): None,
            Unit(UnitTypes.FLEET, 'Skagerrak'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Sweden'): None,
            Unit(UnitTypes.FLEET, 'Skagerrak'): {
                'Denmark Coast',
            },
            Unit(UnitTypes.FLEET, 'Barents Sea'): None,
        },
    }


def test_g_12__swapping_two_units_with_two_convoys():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Liverpool', 'Edinburgh'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Norwegian Sea', 'Liverpool', 'Edinburgh'),
            CommandHelper(
                CommandType.CONVOY_TRANSPORT,
                UnitTypes.FLEET,
                'North Atlantic Ocean',
                'Liverpool',
                'Edinburgh',
            ),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Edinburgh', 'Liverpool'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'North Sea', 'Edinburgh', 'Liverpool'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'Edinburgh', 'Liverpool'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Irish Sea', 'Edinburgh', 'Liverpool'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Edinburgh'): None,
            Unit(UnitTypes.FLEET, 'North Atlantic Ocean'): None,
            Unit(UnitTypes.FLEET, 'Norwegian Sea'): None,
        },
        'Germany': {
            Unit(UnitTypes.TROOP, 'Liverpool'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): None,
            Unit(UnitTypes.FLEET, 'English Channel'): None,
            Unit(UnitTypes.FLEET, 'Irish Sea'): None,
        },
    }


def test_g_13__support_cut_on_attack_on_itself_via_convoy():
    helper = TurnHelper([
        PlayerHelper('Austria', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Trieste', 'Venice'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Adriatic Sea', 'Trieste', 'Venice'),
        ]),
        PlayerHelper('Italy', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Albania Coast', 'Trieste Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Venice', 'Albania Coast', 'Trieste Coast'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'Austria': {
            Unit(UnitTypes.TROOP, 'Trieste'): {
                'Serbia',
                'Budapest',
                'Vienna',
                'Tyrolia',
            },
            Unit(UnitTypes.FLEET, 'Adriatic Sea'): None,
        },
        'Italy': {
            Unit(UnitTypes.TROOP, 'Venice'): None,
            Unit(UnitTypes.FLEET, 'Trieste Coast'): None,
        },
    }


def test_g_14__bounce_by_convoy_to_adjacent_place():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Norway', 'Sweden'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Denmark Coast', 'Norway', 'Sweden'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Finland Coast', 'Norway', 'Sweden'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Skagerrak', 'Sweden', 'Norway'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Sweden', 'Norway'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Barents Sea', 'Sweden', 'Norway'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Norwegian Sea', 'Norway Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'North Sea', 'Norwegian Sea', 'Norway Coast'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Sweden'): None,
            Unit(UnitTypes.FLEET, 'Denmark Coast'): None,
            Unit(UnitTypes.FLEET, 'Finland Coast'): None,
        },
        'Germany': {
            Unit(UnitTypes.FLEET, 'Skagerrak'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Sweden'): set(),
            Unit(UnitTypes.FLEET, 'Barents Sea'): None,
        },
        'France': {
            Unit(UnitTypes.FLEET, 'Norwegian Sea'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): None,
        },
    }


def test_g_15__bounce_and_dislodge_with_double_convoy():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'London', 'Belgium'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'North Sea', 'London', 'Belgium'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Holland', 'London', 'Belgium'),
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Yorkshire', 'London'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Belgium', 'London'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'Belgium', 'London'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Belgium'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): None,
            Unit(UnitTypes.TROOP, 'Holland'): None,
            Unit(UnitTypes.TROOP, 'Yorkshire'): None,
        },
        'France': {
            Unit(UnitTypes.TROOP, 'Belgium'): {
                'Picardy',
                'Burgundy',
                'Ruhr',
            },
            Unit(UnitTypes.FLEET, 'English Channel'): None,
        },
    }


def test_g_16__the_two_unit_in_one_area_bug_moving_by_convoy():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Norway', 'Sweden'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Denmark', 'Norway', 'Sweden'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Baltic Sea', 'Norway', 'Sweden'),
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'North Sea', 'Norway Coast'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Sweden', 'Norway'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Skagerrak', 'Sweden', 'Norway'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Norwegian Sea', 'Sweden', 'Norway'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Sweden'): None,
            Unit(UnitTypes.TROOP, 'Denmark'): None,
            Unit(UnitTypes.FLEET, 'Baltic Sea'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Norway'): None,
            Unit(UnitTypes.FLEET, 'Skagerrak'): None,
            Unit(UnitTypes.FLEET, 'Norwegian Sea'): None,
        },
    }


def test_g_17__the_two_unit_in_one_area_bug_moving_over_land():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Norway', 'Sweden'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Skagerrak', 'Norway', 'Sweden'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Denmark', 'Norway', 'Sweden'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Baltic Sea', 'Norway', 'Sweden'),
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'North Sea', 'Norway Coast'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Sweden', 'Norway'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Norwegian Sea', 'Sweden', 'Norway'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Sweden'): None,
            Unit(UnitTypes.FLEET, 'Skagerrak'): None,
            Unit(UnitTypes.TROOP, 'Denmark'): None,
            Unit(UnitTypes.FLEET, 'Baltic Sea'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Norway'): None,
            Unit(UnitTypes.FLEET, 'Norwegian Sea'): None,
        },
    }


def test_g_18__the_two_unit_in_one_area_bug_with_double_convoy():

    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'London', 'Belgium'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'North Sea', 'London', 'Belgium'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Holland', 'London', 'Belgium'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Ruhr', 'London', 'Belgium'),
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Yorkshire', 'London'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Belgium', 'London'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'English Channel', 'Belgium', 'London'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Wales', 'Belgium', 'London'),
        ]),
    ])
    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Belgium'): None,
            Unit(UnitTypes.FLEET, 'North Sea'): None,
            Unit(UnitTypes.TROOP, 'Holland'): None,
            Unit(UnitTypes.TROOP, 'Ruhr'): None,
            Unit(UnitTypes.TROOP, 'Yorkshire'): None,
        },
        'France': {
            Unit(UnitTypes.TROOP, 'London'): None,
            Unit(UnitTypes.FLEET, 'English Channel'): None,
            Unit(UnitTypes.TROOP, 'Wales'): None,
        },
    }
