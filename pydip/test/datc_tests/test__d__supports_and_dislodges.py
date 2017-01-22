import pytest

from pydip.map.predefined.vanilla_dip import generate_map
from pydip.player.command.command import SupportCommand
from pydip.player.player import Player
from pydip.player.unit import Unit, UnitTypes
from pydip.test.command_helper import CommandType, CommandHelper
from pydip.test.player_helper import PlayerHelper
from pydip.test.turn_helper import TurnHelper


def test_d_1__supported_hold_can_prevent_dislodgement():
    helper = TurnHelper([
        PlayerHelper('Austria', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Trieste', 'Venice'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Adriatic Sea', 'Trieste', 'Venice'),
        ]),
        PlayerHelper('Italy', [
            CommandHelper(CommandType.HOLD, UnitTypes.TROOP, 'Venice'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Tyrolia', 'Venice', 'Venice'),
        ])
    ])

    result = helper.resolve()
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
    helper = TurnHelper([
        PlayerHelper('Austria', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Trieste', 'Venice'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Adriatic Sea', 'Trieste', 'Venice'),
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Vienna', 'Tyrolia'),
        ]),
        PlayerHelper('Italy', [
            CommandHelper(CommandType.HOLD, UnitTypes.TROOP, 'Venice'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Tyrolia', 'Venice', 'Venice'),
        ])
    ])

    result = helper.resolve()
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
    helper = TurnHelper([
        PlayerHelper('Austria', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Trieste', 'Venice'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Adriatic Sea', 'Trieste', 'Venice'),
        ]),
        PlayerHelper('Italy', [
            CommandHelper(CommandType.HOLD, UnitTypes.TROOP, 'Venice'),
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Ionian Sea', 'Adriatic Sea'),
        ])
    ])

    result = helper.resolve()
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
    helper = TurnHelper([
        PlayerHelper('Germany', [
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Berlin', 'Kiel Coast', 'Kiel Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Kiel Coast', 'Berlin', 'Berlin'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Prussia', 'Berlin'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Baltic Sea', 'Prussia', 'Berlin'),
        ])
    ])

    result = helper.resolve()
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
    helper = TurnHelper([
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Munich', 'Silesia'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Berlin', 'Munich', 'Silesia'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Kiel Coast', 'Berlin', 'Berlin'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Prussia', 'Berlin'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Baltic Sea', 'Prussia', 'Berlin'),
        ])
    ])

    result = helper.resolve()
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
    helper = TurnHelper([
        PlayerHelper('Germany', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Berlin', 'Sweden'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Baltic Sea', 'Berlin', 'Sweden'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Prussia Coast', 'Baltic Sea', 'Baltic Sea'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Livonia Coast', 'Baltic Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Gulf of Bothnia', 'Livonia Coast', 'Baltic Sea'),
        ])
    ])

    result = helper.resolve()
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
    helper = TurnHelper([
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Baltic Sea', 'Sweden Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Prussia Coast', 'Baltic Sea', 'Baltic Sea'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Livonia Coast', 'Baltic Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Gulf of Bothnia', 'Livonia Coast', 'Baltic Sea'),
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Finland', 'Sweden'),
        ])
    ])

    result = helper.resolve()
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
    helper = TurnHelper([
        PlayerHelper('Austria', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Albania', 'Greece'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Serbia', 'Albania', 'Greece'),
        ]),
        PlayerHelper('Turkey', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Greece', 'Naples'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Bulgaria', 'Greece', 'Greece'),
        ])
    ])

    result = helper.resolve()
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
    helper = TurnHelper([
        PlayerHelper('Austria', [
            CommandHelper(CommandType.HOLD, UnitTypes.TROOP, 'Trieste'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Albania', 'Trieste', 'Serbia'),
        ]),
        PlayerHelper('Italy', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Venice', 'Trieste'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Tyrolia', 'Venice', 'Trieste'),
        ])
    ])

    result = helper.resolve()
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
    helper = TurnHelper([
        PlayerHelper('Germany', [
            CommandHelper(CommandType.HOLD, UnitTypes.TROOP, 'Berlin'),
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Kiel Coast', 'Berlin Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Munich', 'Kiel Coast', 'Berlin Coast'),
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


def test_d_11__no_self_dislodgement_of_returning_unit():
    helper = TurnHelper([
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Berlin', 'Prussia'),
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Kiel Coast', 'Berlin Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Munich', 'Kiel Coast', 'Berlin Coast'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Warsaw', 'Prussia'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'Germany': {
            Unit(UnitTypes.TROOP, 'Berlin'): None,
            Unit(UnitTypes.FLEET, 'Kiel Coast'): None,
            Unit(UnitTypes.TROOP, 'Munich'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Warsaw'): None,
        },
    }


def test_d_12__supporing_foreign_unit_to_dislodge_own_unit_prohibited():
    helper = TurnHelper([
        PlayerHelper('Austria', [
            CommandHelper(CommandType.HOLD, UnitTypes.FLEET, 'Trieste Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Vienna', 'Venice', 'Trieste'),
        ]),
        PlayerHelper('Italy', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Venice', 'Trieste'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'Austria': {
            Unit(UnitTypes.FLEET, 'Trieste Coast'): None,
            Unit(UnitTypes.TROOP, 'Vienna'): None,
        },
        'Italy': {
            Unit(UnitTypes.TROOP, 'Venice'): None,
        },
    }


def test_d_13__supporing_foreign_unit_to_dislodge_returning_own_unit_prohibited():
    helper = TurnHelper([
        PlayerHelper('Austria', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Trieste Coast', 'Adriatic Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Vienna', 'Venice', 'Trieste'),
        ]),
        PlayerHelper('Italy', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Venice', 'Trieste'),
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Apulia Coast', 'Adriatic Sea'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'Austria': {
            Unit(UnitTypes.FLEET, 'Trieste Coast'): None,
            Unit(UnitTypes.TROOP, 'Vienna'): None,
        },
        'Italy': {
            Unit(UnitTypes.TROOP, 'Venice'): None,
            Unit(UnitTypes.FLEET, 'Apulia Coast'): None,
        },
    }


def test_d_14__supporing_foreign_unit_not_enough_to_prevent_dislodgement():
    helper = TurnHelper([
        PlayerHelper('Austria', [
            CommandHelper(CommandType.HOLD, UnitTypes.FLEET, 'Trieste Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Vienna', 'Venice', 'Trieste'),
        ]),
        PlayerHelper('Italy', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Venice', 'Trieste'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Tyrolia', 'Venice', 'Trieste'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Adriatic Sea', 'Venice', 'Trieste'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'Austria': {
            Unit(UnitTypes.FLEET, 'Trieste Coast'): {
                'Albania Coast',
            },
            Unit(UnitTypes.TROOP, 'Vienna'): None,
        },
        'Italy': {
            Unit(UnitTypes.TROOP, 'Trieste'): None,
            Unit(UnitTypes.TROOP, 'Tyrolia'): None,
            Unit(UnitTypes.FLEET, 'Adriatic Sea'): None,
        },
    }


def test_d_15__defender_cannot_cut_support_for_attack_on_itself():
    helper = TurnHelper([
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Black Sea', 'Ankara Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Constantinople Coast', 'Black Sea', 'Ankara Coast'),
        ]),
        PlayerHelper('Turkey', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Ankara Coast', 'Constantinople Coast'),
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


def test_d_16__convoying_a_unit_dislodging_a_unit_of_same_power_is_allowed():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.HOLD, UnitTypes.TROOP, 'London'),
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'North Sea', 'Belgium', 'London'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Belgium', 'London'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'English Channel', 'Belgium', 'London'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'London'): {
                'Yorkshire',
                'Wales',
            },
            Unit(UnitTypes.FLEET, 'North Sea'): None,
        },
        'France': {
            Unit(UnitTypes.FLEET, 'English Channel'): None,
            Unit(UnitTypes.TROOP, 'London'): None,
        },
    }


def test_d_17__dislodgement_cuts_supports():
    helper = TurnHelper([
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Black Sea', 'Ankara Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Constantinople Coast', 'Black Sea', 'Ankara Coast'),
        ]),
        PlayerHelper('Turkey', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Ankara Coast', 'Constantinople Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Smyrna', 'Ankara Coast', 'Constantinople Coast'),
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Armenia', 'Ankara'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'Russia': {
            Unit(UnitTypes.FLEET, 'Black Sea'): None,
            Unit(UnitTypes.FLEET, 'Constantinople Coast'): {
                'Bulgaria North Coast',
                'Bulgaria South Coast',
                'Aegean Sea',
            },
        },
        'Turkey': {
            Unit(UnitTypes.FLEET, 'Constantinople Coast'): None,
            Unit(UnitTypes.TROOP, 'Smyrna'): None,
            Unit(UnitTypes.TROOP, 'Armenia'): None,
        },
    }


def test_d_18__a_surviving_unit_will_sustain_support():
    helper = TurnHelper([
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Black Sea', 'Ankara Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Constantinople Coast', 'Black Sea', 'Ankara Coast'),
            CommandHelper(
                CommandType.SUPPORT,
                UnitTypes.TROOP,
                'Bulgaria',
                'Constantinople Coast',
                'Constantinople Coast',
            ),
        ]),
        PlayerHelper('Turkey', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Ankara Coast', 'Constantinople Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Smyrna', 'Ankara Coast', 'Constantinople Coast'),
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Armenia', 'Ankara'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'Russia': {
            Unit(UnitTypes.FLEET, 'Ankara Coast'): None,
            Unit(UnitTypes.FLEET, 'Constantinople Coast'): None,
            Unit(UnitTypes.TROOP, 'Bulgaria'): None,
        },
        'Turkey': {
            Unit(UnitTypes.FLEET, 'Ankara Coast'): set(),
            Unit(UnitTypes.TROOP, 'Smyrna'): None,
            Unit(UnitTypes.TROOP, 'Armenia'): None,
        },
    }


def test_d_19__even_when_surviving_is_an_alternative_way():
    helper = TurnHelper([
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Black Sea', 'Ankara Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Constantinople Coast', 'Black Sea', 'Ankara Coast'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Smyrna', 'Ankara Coast', 'Constantinople Coast'),
        ]),
        PlayerHelper('Turkey', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Ankara Coast', 'Constantinople Coast'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'Russia': {
            Unit(UnitTypes.FLEET, 'Ankara Coast'): None,
            Unit(UnitTypes.FLEET, 'Constantinople Coast'): None,
            Unit(UnitTypes.TROOP, 'Smyrna'): None,
        },
        'Turkey': {
            Unit(UnitTypes.FLEET, 'Ankara Coast'): {
                'Armenia Coast',
            },
        },
    }


def test_d_20__unit_cannot_cut_support_of_own_country():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'North Sea', 'English Channel'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'London Coast', 'North Sea', 'English Channel'),
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Yorkshire', 'London'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.HOLD, UnitTypes.FLEET, 'English Channel'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.FLEET, 'English Channel'): None,
            Unit(UnitTypes.FLEET, 'London Coast'): None,
            Unit(UnitTypes.TROOP, 'Yorkshire'): None,
        },
        'France': {
            Unit(UnitTypes.FLEET, 'English Channel'): {
                'Wales Coast',
                'Irish Sea',
                'Mid-Atlantic Ocean',
                'Brest Coast',
                'Picardy Coast',
                'Belgium Coast',
            },
        },
    }


def test_d_21__dislodging_does_not_cancel_support_cut():
    helper = TurnHelper([
        PlayerHelper('Austria', [
            CommandHelper(CommandType.HOLD, UnitTypes.FLEET, 'Trieste Coast'),
        ]),
        PlayerHelper('Italy', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Venice', 'Trieste'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Tyrolia', 'Venice', 'Trieste'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Munich', 'Tyrolia'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Silesia', 'Munich'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Berlin', 'Silesia', 'Munich'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'Austria': {
            Unit(UnitTypes.FLEET, 'Trieste Coast'): None,
        },
        'Italy': {
            Unit(UnitTypes.TROOP, 'Venice'): None,
            Unit(UnitTypes.TROOP, 'Tyrolia'): None,
        },
        'Germany': {
            Unit(UnitTypes.TROOP, 'Munich'): {
                'Bohemia',
                'Burgundy',
                'Ruhr',
                'Kiel',
            },
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Munich'): None,
            Unit(UnitTypes.TROOP, 'Berlin'): None,
        },
    }


def test_d_22__impossible_fleet_move_cannot_be_supported():
    """
    Adapted from DATC test, because the DATC test requires illegal moves to be
    specified, which this system prevents
    """
    game_map = generate_map()
    germany_starting_configuration = [
        {'territory_name': 'Kiel Coast', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Burgundy', 'unit_type': UnitTypes.TROOP},
    ]
    germany = Player("Germany", game_map, germany_starting_configuration)

    with pytest.raises(AssertionError):
        SupportCommand(germany, germany.units[1], germany.units[0], 'Munich')


def test_d_23__impossible_coast_move_can_not_be_supported():
    """
    Adapted from DATC test, because the DATC test requires illegal moves to be
    specified, which this system prevents
    """
    game_map = generate_map()
    france_starting_configuration = [
        {'territory_name': 'Spain North Coast', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Marseilles Coast', 'unit_type': UnitTypes.FLEET},
    ]
    france = Player("France", game_map, france_starting_configuration)

    with pytest.raises(AssertionError):
        SupportCommand(france, france.units[1], france.units[0], 'Gulf of Lyon')


def test_d_24__impossible_army_move_cannot_be_supported():
    """
    Adapted from DATC test, because the DATC test requires illegal moves to be
    specified, which this system prevents
    """
    game_map = generate_map()
    france_starting_configuration = [
        {'territory_name': 'Marseilles', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Spain South Coast', 'unit_type': UnitTypes.FLEET},
    ]
    france = Player("France", game_map, france_starting_configuration)

    with pytest.raises(AssertionError):
        SupportCommand(france, france.units[1], france.units[0], 'Gulf of Lyon')


def test_d_25__impossible_army_move_cannot_be_supported():
    helper = TurnHelper([
        PlayerHelper('Germany', [
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Berlin', 'Prussia', 'Prussia'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Kiel Coast', 'Berlin', 'Berlin'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Prussia', 'Berlin'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Baltic Sea', 'Prussia', 'Berlin'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'Germany': {
            Unit(UnitTypes.TROOP, 'Berlin'): None,
            Unit(UnitTypes.FLEET, 'Kiel Coast'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Prussia'): None,
            Unit(UnitTypes.FLEET, 'Baltic Sea'): None,
        },
    }


def test_d_26__failing_move_support_can_be_supported():
    helper = TurnHelper([
        PlayerHelper('Germany', [
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Berlin', 'Prussia', 'Silesia'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Kiel Coast', 'Berlin', 'Berlin'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Prussia', 'Berlin'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Baltic Sea', 'Prussia', 'Berlin'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'Germany': {
            Unit(UnitTypes.TROOP, 'Berlin'): None,
            Unit(UnitTypes.FLEET, 'Kiel Coast'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Prussia'): None,
            Unit(UnitTypes.FLEET, 'Baltic Sea'): None,
        },
    }


def test_d_27__failing_convoy_can_be_supported():
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Sweden Coast', 'Baltic Sea'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Denmark Coast', 'Sweden Coast', 'Baltic Sea'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.HOLD, UnitTypes.TROOP, 'Berlin'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.CONVOY_TRANSPORT, UnitTypes.FLEET, 'Baltic Sea', 'Berlin', 'Livonia'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Prussia Coast', 'Baltic Sea', 'Baltic Sea'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.FLEET, 'Sweden Coast'): None,
            Unit(UnitTypes.FLEET, 'Denmark Coast'): None,
        },
        'Germany': {
            Unit(UnitTypes.TROOP, 'Berlin'): None,
        },
        'Russia': {
            Unit(UnitTypes.FLEET, 'Baltic Sea'): None,
            Unit(UnitTypes.FLEET, 'Prussia Coast'): None,
        },
    }


# Tests D.28, D.29, and D.30 are skipped due to relying on illegal commands that are
# not possible in this system

def test_d_31__tricky_impossible_support():
    """
    Adapted from D.31, because I disagree that preventing this move specification is critical,
    but more a nice-to-have. For the time being, we'll permit and acknowledge this support is
    not very helpful.
    """
    helper = TurnHelper([
        PlayerHelper('Austria', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Rumania', 'Armenia'),
        ]),
        PlayerHelper('Turkey', [
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Black Sea', 'Rumania', 'Armenia'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'Austria': {
            Unit(UnitTypes.TROOP, 'Rumania'): None,
        },
        'Turkey': {
            Unit(UnitTypes.FLEET, 'Black Sea'): None,
        },
    }


def test_d_32__a_missing_fleet():
    """
    Adapted from D.32, because I disagree that preventing this move specification is critical,
    but more a nice-to-have. I DEFINITELY do not think this should be treated as illegal at
    resolution time, and that if these commands are issued, they should be treated as-is.
    Support from France fails.
    """
    helper = TurnHelper([
        PlayerHelper('England', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Liverpool', 'Yorkshire'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Edinburgh Coast', 'Liverpool', 'Yorkshire'),
        ]),
        PlayerHelper('France', [
            CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'London Coast', 'Yorkshire', 'Yorkshire'),
        ]),
        PlayerHelper('Germany', [
            CommandHelper(CommandType.CONVOY_MOVE, UnitTypes.TROOP, 'Yorkshire', 'Holland'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'England': {
            Unit(UnitTypes.TROOP, 'Yorkshire'): None,
            Unit(UnitTypes.FLEET, 'Edinburgh Coast'): None,
        },
        'France': {
            Unit(UnitTypes.FLEET, 'London Coast'): None,
        },
        'Germany': {
            Unit(UnitTypes.TROOP, 'Yorkshire'): {
                'Wales',
            },
        },
    }


def test_d_33__unwanted_support_allowed():
    helper = TurnHelper([
        PlayerHelper('Austria', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Serbia', 'Budapest'),
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Vienna', 'Budapest'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Galicia', 'Serbia', 'Budapest'),
        ]),
        PlayerHelper('Turkey', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Bulgaria', 'Serbia'),
        ])
    ])

    result = helper.resolve()
    assert result == {
        'Austria': {
            Unit(UnitTypes.TROOP, 'Budapest'): None,
            Unit(UnitTypes.TROOP, 'Vienna'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Galicia'): None,
        },
        'Turkey': {
            Unit(UnitTypes.TROOP, 'Serbia'): None,
        },
    }


def test_d_34__support_targetting_own_area_not_allowed():
    """
    Adapted from DATC test, because the DATC test requires illegal moves to be
    specified, which this system prevents
    """
    game_map = generate_map()
    italy_starting_configuration = [
        {'territory_name': 'Prussia', 'unit_type': UnitTypes.TROOP},
    ]
    italy = Player("Italy", game_map, italy_starting_configuration)

    russia_starting_configuration = [
        {'territory_name': 'Warsaw', 'unit_type': UnitTypes.TROOP},
    ]
    russia = Player("Russia", game_map, russia_starting_configuration)

    with pytest.raises(AssertionError):
        SupportCommand(italy, italy.units[0], russia.units[0], 'Prussia')
