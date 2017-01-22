from pydip.player.unit import Unit, UnitTypes
from pydip.test.command_helper import CommandType, CommandHelper
from pydip.test.player_helper import PlayerHelper
from pydip.test.turn_helper import TurnHelper


def test_e_1__dislodged_unit_has_no_effect_on_attackers_area():
    helper = TurnHelper([
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Berlin', 'Prussia'),
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Kiel Coast', 'Berlin Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Silesia', 'Berlin', 'Prussia'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Prussia', 'Berlin'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'Germany': {
            Unit(UnitTypes.TROOP, 'Prussia'): None,
            Unit(UnitTypes.FLEET, 'Berlin Coast'): None,
            Unit(UnitTypes.TROOP, 'Silesia'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Prussia'): {
                'Warsaw',
                'Livonia',
            },
        },
    }


def test_e_2__no_self_dislodgement_in_head_to_head_battle():
    helper = TurnHelper([
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Berlin', 'Kiel'),
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Kiel Coast', 'Berlin Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Munich', 'Berlin', 'Kiel'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'Germany': {
            Unit(UnitTypes.TROOP, 'Berlin'): None,
            Unit(UnitTypes.FLEET, 'Kiel Coast'): None,
            Unit(UnitTypes.TROOP, 'Munich'): None,
        },
    }


def test_e_3__no_help_in_dislodging_own_unit():
    helper = TurnHelper([
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Berlin', 'Kiel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Munich', 'Kiel Coast', 'Berlin Coast'),
        ]),
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Kiel Coast', 'Berlin Coast'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'Germany': {
            Unit(UnitTypes.TROOP, 'Berlin'): None,
            Unit(UnitTypes.TROOP, 'Munich'): None,
        },
        'England': {
            Unit(UnitTypes.FLEET, 'Kiel Coast'): None,
        }
    }


def test_e_4__non_dislodged_loser_still_has_effect():
    helper = TurnHelper([
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Holland Coast', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Helgoland Bight', 'Holland Coast', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Skagerrak', 'Holland Coast', 'North Sea'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'North Sea', 'Holland Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Belgium Coast', 'North Sea', 'Holland Coast'),
        ]),
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Norwegian Sea', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Edinburgh Coast', 'Norwegian Sea', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Yorkshire Coast', 'Norwegian Sea', 'North Sea'),
        ]),
        PlayerHelper('Austria', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Ruhr', 'Holland'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Kiel', 'Ruhr', 'Holland'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'Germany': {
            Unit(UnitTypes.FLEET, 'Holland Coast'): None,
            Unit(UnitTypes.FLEET, 'Helgoland Bight'): None,
            Unit(UnitTypes.FLEET, 'Skagerrak'): None,
        },
        'France': {
            Unit(UnitTypes.FLEET, 'North Sea'): None,
            Unit(UnitTypes.FLEET, 'Belgium Coast'): None,
        },
        'England': {
            Unit(UnitTypes.FLEET, 'Norwegian Sea'): None,
            Unit(UnitTypes.FLEET, 'Edinburgh Coast'): None,
            Unit(UnitTypes.FLEET, 'Yorkshire Coast'): None,
        },
        'Austria': {
            Unit(UnitTypes.TROOP, 'Ruhr'): None,
            Unit(UnitTypes.TROOP, 'Kiel'): None,
        }
    }


def test_e_5__loser_dislodged_by_another_army_still_has_effect():
    helper = TurnHelper([
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Holland Coast', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Helgoland Bight', 'Holland Coast', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Skagerrak', 'Holland Coast', 'North Sea'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'North Sea', 'Holland Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Belgium Coast', 'North Sea', 'Holland Coast'),
        ]),
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Norwegian Sea', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Edinburgh Coast', 'Norwegian Sea', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Yorkshire Coast', 'Norwegian Sea', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'London Coast', 'Norwegian Sea', 'North Sea'),
        ]),
        PlayerHelper('Austria', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Ruhr', 'Holland'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Kiel', 'Ruhr', 'Holland'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'Germany': {
            Unit(UnitTypes.FLEET, 'Holland Coast'): None,
            Unit(UnitTypes.FLEET, 'Helgoland Bight'): None,
            Unit(UnitTypes.FLEET, 'Skagerrak'): None,
        },
        'France': {
            Unit(UnitTypes.FLEET, 'North Sea'): {
                'English Channel',
                'Denmark Coast',
                'Norway Coast',
            },
            Unit(UnitTypes.FLEET, 'Belgium Coast'): None,
        },
        'England': {
            Unit(UnitTypes.FLEET, 'North Sea'): None,
            Unit(UnitTypes.FLEET, 'Edinburgh Coast'): None,
            Unit(UnitTypes.FLEET, 'Yorkshire Coast'): None,
            Unit(UnitTypes.FLEET, 'London Coast'): None,
        },
        'Austria': {
            Unit(UnitTypes.TROOP, 'Ruhr'): None,
            Unit(UnitTypes.TROOP, 'Kiel'): None,
        }
    }


def test_e_6__not_dislodged_because_of_own_support_still_has_effect():
    helper = TurnHelper([
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Holland Coast', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Helgoland Bight', 'Holland Coast', 'North Sea'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'North Sea', 'Holland Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Belgium Coast', 'North Sea', 'Holland Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'English Channel', 'Holland Coast', 'North Sea'),
        ]),
        PlayerHelper('Austria', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Ruhr', 'Holland'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Kiel', 'Ruhr', 'Holland'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'Germany': {
            Unit(UnitTypes.FLEET, 'Holland Coast'): None,
            Unit(UnitTypes.FLEET, 'Helgoland Bight'): None,
        },
        'France': {
            Unit(UnitTypes.FLEET, 'North Sea'): None,
            Unit(UnitTypes.FLEET, 'Belgium Coast'): None,
            Unit(UnitTypes.FLEET, 'English Channel'): None,
        },
        'Austria': {
            Unit(UnitTypes.TROOP, 'Ruhr'): None,
            Unit(UnitTypes.TROOP, 'Kiel'): None,
        }
    }


def test_e_7__no_self_dislodgement_with_beleaguered_garrison():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.HOLD, UnitTypes.FLEET, 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Yorkshire Coast', 'Norway Coast', 'North Sea'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Helgoland Bight', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Holland Coast', 'Helgoland Bight', 'North Sea'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Norway Coast', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Skagerrak', 'Norway Coast', 'North Sea'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.FLEET, 'North Sea'): None,
            Unit(UnitTypes.FLEET, 'Yorkshire Coast'): None,
        },
        'Germany': {
            Unit(UnitTypes.FLEET, 'Holland Coast'): None,
            Unit(UnitTypes.FLEET, 'Helgoland Bight'): None,
        },
        'Russia': {
            Unit(UnitTypes.FLEET, 'Norway Coast'): None,
            Unit(UnitTypes.FLEET, 'Skagerrak'): None,
        }
    }


def test_e_8__no_self_dislodgement_with_beleaguered_garrison_and_head_to_head_battle():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'North Sea', 'Norway Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Yorkshire Coast', 'Norway Coast', 'North Sea'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Helgoland Bight', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Holland Coast', 'Helgoland Bight', 'North Sea'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Norway Coast', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Skagerrak', 'Norway Coast', 'North Sea'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.FLEET, 'North Sea'): None,
            Unit(UnitTypes.FLEET, 'Yorkshire Coast'): None,
        },
        'Germany': {
            Unit(UnitTypes.FLEET, 'Holland Coast'): None,
            Unit(UnitTypes.FLEET, 'Helgoland Bight'): None,
        },
        'Russia': {
            Unit(UnitTypes.FLEET, 'Norway Coast'): None,
            Unit(UnitTypes.FLEET, 'Skagerrak'): None,
        }
    }


def test_e_9__almost_self_dislodgement_with_beleaguered_garrison():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'North Sea', 'Norwegian Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Yorkshire Coast', 'Norway Coast', 'North Sea'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Helgoland Bight', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Holland Coast', 'Helgoland Bight', 'North Sea'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Norway Coast', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Skagerrak', 'Norway Coast', 'North Sea'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.FLEET, 'Norwegian Sea'): None,
            Unit(UnitTypes.FLEET, 'Yorkshire Coast'): None,
        },
        'Germany': {
            Unit(UnitTypes.FLEET, 'Holland Coast'): None,
            Unit(UnitTypes.FLEET, 'Helgoland Bight'): None,
        },
        'Russia': {
            Unit(UnitTypes.FLEET, 'North Sea'): None,
            Unit(UnitTypes.FLEET, 'Skagerrak'): None,
        }
    }


def test_e_10__almost_circular_movement_with_no_self_dislodgement_with_beleaguered_garrison():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'North Sea', 'Denmark Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Yorkshire Coast', 'Norway Coast', 'North Sea'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Helgoland Bight', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Holland Coast', 'Helgoland Bight', 'North Sea'),
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Denmark Coast', 'Helgoland Bight'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Norway Coast', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Skagerrak', 'Norway Coast', 'North Sea'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.FLEET, 'North Sea'): None,
            Unit(UnitTypes.FLEET, 'Yorkshire Coast'): None,
        },
        'Germany': {
            Unit(UnitTypes.FLEET, 'Holland Coast'): None,
            Unit(UnitTypes.FLEET, 'Helgoland Bight'): None,
            Unit(UnitTypes.FLEET, 'Denmark Coast'): None,
        },
        'Russia': {
            Unit(UnitTypes.FLEET, 'Norway Coast'): None,
            Unit(UnitTypes.FLEET, 'Skagerrak'): None,
        }
    }


def test_e_11__no_self_dislodgement_with_beleaguered_garrison_unit_swap_with_adjacent_convoying_and_two_coasts():
    helper = TurnHelper([
        PlayerHelper('France', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Spain', 'Portugal'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Mid-Atlantic Ocean', 'Spain', 'Portugal'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Gulf of Lyon', 'Portugal Coast', 'Spain North Coast'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Gascony', 'Spain'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Marseilles', 'Gascony', 'Spain'),
        ]),
        PlayerHelper('Italy', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Portugal Coast', 'Spain North Coast'),
            CommandHelper(
                CommandType.SUPPORT,
                UnitTypes.FLEET,
                'Western Mediterranean Sea',
                'Portugal Coast',
                'Spain North Coast',
            ),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'France': {
            Unit(UnitTypes.TROOP, 'Portugal'): None,
            Unit(UnitTypes.FLEET, 'Mid-Atlantic Ocean'): None,
            Unit(UnitTypes.FLEET, 'Gulf of Lyon'): None,
        },
        'Germany': {
            Unit(UnitTypes.TROOP, 'Gascony'): None,
            Unit(UnitTypes.TROOP, 'Marseilles'): None,
        },
        'Italy': {
            Unit(UnitTypes.FLEET, 'Spain North Coast'): None,
            Unit(UnitTypes.FLEET, 'Western Mediterranean Sea'): None,
        }
    }


def test_e_12__support_on_attack_on_own_unit_can_be_used_for_other_means():
    helper = TurnHelper([
        PlayerHelper('Austria', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Budapest', 'Rumania'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Serbia', 'Vienna', 'Budapest'),
        ]),
        PlayerHelper('Italy', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Vienna', 'Budapest'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Galicia', 'Budapest'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Rumania', 'Galicia', 'Budapest'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'Austria': {
            Unit(UnitTypes.TROOP, 'Budapest'): None,
            Unit(UnitTypes.TROOP, 'Serbia'): None,
        },
        'Italy': {
            Unit(UnitTypes.TROOP, 'Vienna'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Galicia'): None,
            Unit(UnitTypes.TROOP, 'Rumania'): None,
        }
    }


def test_e_13__three_way_beleaguered_garrison():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Yorkshire Coast', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Edinburgh Coast', 'Yorkshire Coast', 'North Sea'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Belgium Coast', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'English Channel', 'Belgium Coast', 'North Sea'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.HOLD, UnitTypes.FLEET, 'North Sea'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Norwegian Sea', 'North Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Norway Coast', 'Norwegian Sea', 'North Sea'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.FLEET, 'Yorkshire Coast'): None,
            Unit(UnitTypes.FLEET, 'Edinburgh Coast'): None,
        },
        'France': {
            Unit(UnitTypes.FLEET, 'Belgium Coast'): None,
            Unit(UnitTypes.FLEET, 'English Channel'): None,
        },
        'Germany': {
            Unit(UnitTypes.FLEET, 'North Sea'): None,
        },
        'Russia': {
            Unit(UnitTypes.FLEET, 'Norwegian Sea'): None,
            Unit(UnitTypes.FLEET, 'Norway Coast'): None,
        }
    }


# Test E.14 is skipped, because it relies on an illegal move that this system disallows


def test_e_15__the_friendly_head_to_head_battle():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Ruhr', 'Kiel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Holland Coast', 'Ruhr', 'Kiel'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Kiel', 'Berlin'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Munich', 'Kiel', 'Berlin'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Silesia', 'Kiel', 'Berlin'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Berlin', 'Kiel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Denmark Coast', 'Berlin', 'Kiel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Helgoland Bight', 'Berlin', 'Kiel'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Prussia', 'Berlin'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Baltic Sea', 'Prussia', 'Berlin'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Ruhr'): None,
            Unit(UnitTypes.FLEET, 'Holland Coast'): None,
        },
        'France': {
            Unit(UnitTypes.TROOP, 'Kiel'): None,
            Unit(UnitTypes.TROOP, 'Munich'): None,
            Unit(UnitTypes.TROOP, 'Silesia'): None,
        },
        'Germany': {
            Unit(UnitTypes.TROOP, 'Berlin'): None,
            Unit(UnitTypes.FLEET, 'Denmark Coast'): None,
            Unit(UnitTypes.FLEET, 'Helgoland Bight'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Prussia'): None,
            Unit(UnitTypes.FLEET, 'Baltic Sea'): None,
        }
    }
