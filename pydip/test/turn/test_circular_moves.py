from pydip.player.unit import Unit, UnitTypes
from pydip.test.command_helper import CommandType, CommandHelper
from pydip.test.player_helper import PlayerHelper
from pydip.test.turn_helper import TurnHelper


def test_three_country_rotation():
    helper = TurnHelper([
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Galicia', 'Bohemia'),
        ]),
        PlayerHelper('Austria', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Bohemia', 'Vienna'),
        ]),
        PlayerHelper('Turkey', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Vienna', 'Galicia'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'Germany': {
            Unit(UnitTypes.TROOP, 'Bohemia'): None,
        },
        'Austria': {
            Unit(UnitTypes.TROOP, 'Vienna'): None,
        },
        'Turkey': {
            Unit(UnitTypes.TROOP, 'Galicia'): None,
        },
    }


def test_three_country_rotation_with_one_move_supported():
    helper = TurnHelper([
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Galicia', 'Bohemia'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Silesia', 'Galicia', 'Bohemia'),
        ]),
        PlayerHelper('Austria', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Bohemia', 'Vienna'),
        ]),
        PlayerHelper('Turkey', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Vienna', 'Galicia'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'Germany': {
            Unit(UnitTypes.TROOP, 'Bohemia'): None,
            Unit(UnitTypes.TROOP, 'Silesia'): None,
        },
        'Austria': {
            Unit(UnitTypes.TROOP, 'Vienna'): None,
        },
        'Turkey': {
            Unit(UnitTypes.TROOP, 'Galicia'): None,
        },
    }


def test_three_country_rotation_with_one_support_each():
    helper = TurnHelper([
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Galicia', 'Bohemia'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Silesia', 'Galicia', 'Bohemia'),
        ]),
        PlayerHelper('Austria', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Bohemia', 'Vienna'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Tyrolia', 'Bohemia', 'Vienna'),
        ]),
        PlayerHelper('Turkey', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Vienna', 'Galicia'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Budapest', 'Vienna', 'Galicia'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'Germany': {
            Unit(UnitTypes.TROOP, 'Bohemia'): None,
            Unit(UnitTypes.TROOP, 'Silesia'): None,
        },
        'Austria': {
            Unit(UnitTypes.TROOP, 'Vienna'): None,
            Unit(UnitTypes.TROOP, 'Tyrolia'): None,
        },
        'Turkey': {
            Unit(UnitTypes.TROOP, 'Galicia'): None,
            Unit(UnitTypes.TROOP, 'Budapest'): None,
        },
    }


def test_three_country_rotation_with_external_disruption():
    helper = TurnHelper([
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Galicia', 'Bohemia'),
        ]),
        PlayerHelper('Austria', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Bohemia', 'Vienna'),
        ]),
        PlayerHelper('Turkey', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Vienna', 'Galicia'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Ukraine', 'Galicia'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'Germany': {
            Unit(UnitTypes.TROOP, 'Galicia'): None,
        },
        'Austria': {
            Unit(UnitTypes.TROOP, 'Bohemia'): None,
        },
        'Turkey': {
            Unit(UnitTypes.TROOP, 'Vienna'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Ukraine'): None,
        },
    }


def test_three_country_rotation_with_external_dislodge():
    helper = TurnHelper([
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Galicia', 'Bohemia'),
        ]),
        PlayerHelper('Austria', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Bohemia', 'Vienna'),
        ]),
        PlayerHelper('Turkey', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Vienna', 'Galicia'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Ukraine', 'Galicia'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Warsaw', 'Ukraine', 'Galicia'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'Germany': {
            Unit(UnitTypes.TROOP, 'Galicia'): {
                'Silesia',
                'Budapest',
                'Rumania',
            },
        },
        'Austria': {
            Unit(UnitTypes.TROOP, 'Bohemia'): None,
        },
        'Turkey': {
            Unit(UnitTypes.TROOP, 'Vienna'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Galicia'): None,
            Unit(UnitTypes.TROOP, 'Warsaw'): None,
        },
    }


def test_three_country_rotation_with_external_disruption_overcome_by_support():
    helper = TurnHelper([
        PlayerHelper('Germany', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Galicia', 'Bohemia'),
        ]),
        PlayerHelper('Austria', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Bohemia', 'Vienna'),
        ]),
        PlayerHelper('Turkey', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Vienna', 'Galicia'),
            CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Budapest', 'Vienna', 'Galicia'),
        ]),
        PlayerHelper('Russia', [
            CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Ukraine', 'Galicia'),
        ]),
    ])

    result = helper.resolve()
    assert result == {
        'Germany': {
            Unit(UnitTypes.TROOP, 'Bohemia'): None,
        },
        'Austria': {
            Unit(UnitTypes.TROOP, 'Vienna'): None,
        },
        'Turkey': {
            Unit(UnitTypes.TROOP, 'Galicia'): None,
            Unit(UnitTypes.TROOP, 'Budapest'): None,
        },
        'Russia': {
            Unit(UnitTypes.TROOP, 'Ukraine'): None,
        },
    }
