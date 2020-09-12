from pydip.player.unit import Unit, UnitTypes
from pydip.test.command_helper import CommandType, CommandHelper
from pydip.test.player_helper import PlayerHelper
from pydip.test.turn_helper import TurnHelper

def test_fleet_cannot_cut_support_from_troop_attacking_into_self():
    helper = TurnHelper([
            PlayerHelper('Italy', [
                CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Bulgaria South Coast', 'Greece Coast'),
            ]),
            PlayerHelper('Austria', [
                CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Serbia', 'Bulgaria'),
                CommandHelper(CommandType.SUPPORT, UnitTypes.TROOP, 'Greece', 'Serbia', 'Bulgaria'),
            ])
        ])

    result = helper.resolve()
    assert result == {
        'Austria': {
            Unit(UnitTypes.TROOP, 'Bulgaria'): None,
            Unit(UnitTypes.TROOP, 'Greece'): None,
        },
        'Italy': {
            Unit(UnitTypes.FLEET, 'Bulgaria South Coast'): {
                'Aegean Sea',
                'Constantinople Coast',
            },
        },
    }

def test_troop_cannot_cut_support_from_fleet_attacking_into_self():
    helper = TurnHelper([
            PlayerHelper('Italy', [
                CommandHelper(CommandType.MOVE, UnitTypes.TROOP, 'Bulgaria', 'Greece'),
            ]),
            PlayerHelper('Austria', [
                CommandHelper(CommandType.MOVE, UnitTypes.FLEET, 'Aegean Sea', 'Bulgaria South Coast'),
                CommandHelper(CommandType.SUPPORT, UnitTypes.FLEET, 'Greece Coast', 'Aegean Sea', 'Bulgaria South Coast'),
            ])
        ])

    result = helper.resolve()
    assert result == {
        'Austria': {
            Unit(UnitTypes.FLEET, 'Bulgaria South Coast'): None,
            Unit(UnitTypes.FLEET, 'Greece Coast'): None,
        },
        'Italy': {
            Unit(UnitTypes.TROOP, 'Bulgaria'): {
                'Serbia',
                'Rumania',
                'Constantinople',
            },
        },
    }