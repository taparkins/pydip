from map.predefined.vanilla_dip import generate_map
from player.command.command import MoveCommand, SupportCommand, HoldCommand, ConvoyMoveCommand, ConvoyTransportCommand
from player.player import Player
from player.unit import Unit, UnitTypes
from test.command_helper import CommandType, CommandHelper
from test.player_helper import PlayerHelper
from test.turn_helper import TurnHelper
from turn.resolve import resolve_turn


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