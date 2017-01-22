from copy import deepcopy

import pytest

from pydip.map.predefined import vanilla_dip
from pydip.player.unit import UnitTypes, Unit
from pydip.test.adjustment_helper import AdjustmentHelper
from pydip.test.command_helper import AdjustmentCommandHelper, AdjustmentCommandType
from pydip.test.player_helper import PlayerHelper


def test_j_1a__too_many_remove_orders__validated():
    """
    This test has been modified from the DATC -- it includes a disband of a unit that does not exist,
    which fails for a completely separate reason, before we even reach order resolution.
    """

    # France has lost one territory to England, all other players have stayed still
    player_units = vanilla_dip.generate_starting_player_units()
    player_units['England'] = {
        Unit(UnitTypes.FLEET, 'English Channel'),
        Unit(UnitTypes.TROOP, 'Brest'),
        Unit(UnitTypes.TROOP, 'Edinburgh'),
    }
    player_units['France'] = {
        Unit(UnitTypes.FLEET, 'Mid-Atlantic Ocean'),
        Unit(UnitTypes.TROOP, 'Paris'),
        Unit(UnitTypes.TROOP, 'Marseilles'),
    }

    helper = AdjustmentHelper(
        [
            PlayerHelper('France', [
                AdjustmentCommandHelper(AdjustmentCommandType.DISBAND, UnitTypes.FLEET, 'Mid-Atlantic Ocean'),
                AdjustmentCommandHelper(AdjustmentCommandType.DISBAND, UnitTypes.TROOP, 'Paris'),
                AdjustmentCommandHelper(AdjustmentCommandType.DISBAND, UnitTypes.TROOP, 'Marseilles'),
            ]),
        ],
        player_units=player_units,
    )

    with pytest.raises(AssertionError):
        helper.resolve__validated()


def test_j_1b__too_many_remove_orders__not_validated():
    """
    This test has been modified from the DATC -- it includes a disband of a unit that does not exist,
    which fails for a completely separate reason, before we even reach order resolution.
    """

    # France has lost one territory to England, all other players have stayed still
    player_units = vanilla_dip.generate_starting_player_units()
    player_units['England'] = {
        Unit(UnitTypes.FLEET, 'English Channel'),
        Unit(UnitTypes.TROOP, 'Brest'),
        Unit(UnitTypes.TROOP, 'Edinburgh'),
    }
    player_units['France'] = {
        Unit(UnitTypes.FLEET, 'Mid-Atlantic Ocean'),
        Unit(UnitTypes.TROOP, 'Paris'),
        Unit(UnitTypes.TROOP, 'Marseilles'),
    }

    helper = AdjustmentHelper(
        [
            PlayerHelper('France', [
                AdjustmentCommandHelper(AdjustmentCommandType.DISBAND, UnitTypes.FLEET, 'Mid-Atlantic Ocean'),
                AdjustmentCommandHelper(AdjustmentCommandType.DISBAND, UnitTypes.TROOP, 'Paris'),
                AdjustmentCommandHelper(AdjustmentCommandType.DISBAND, UnitTypes.TROOP, 'Marseilles'),
            ]),
        ],
        player_units=player_units,
    )

    results = helper.resolve()
    expected_results = deepcopy(player_units)
    expected_results['France'] = {
        Unit(UnitTypes.TROOP, 'Paris'),
        Unit(UnitTypes.TROOP, 'Marseilles'),
    }
    assert results == expected_results


def test_j_2a__removing_the_same_unit_twice__validated():
    # France has lost one territory to England and one to Germany, all other players have stayed still
    player_units = vanilla_dip.generate_starting_player_units()
    player_units['England'] = {
        Unit(UnitTypes.FLEET, 'English Channel'),
        Unit(UnitTypes.TROOP, 'Brest'),
        Unit(UnitTypes.TROOP, 'Edinburgh'),
    }
    player_units['Germany'] = {
        Unit(UnitTypes.FLEET, 'Kiel Coast'),
        Unit(UnitTypes.TROOP, 'Marseilles'),
        Unit(UnitTypes.TROOP, 'Berlin'),
    }
    player_units['France'] = {
        Unit(UnitTypes.FLEET, 'Mid-Atlantic Ocean'),
        Unit(UnitTypes.TROOP, 'Paris'),
        Unit(UnitTypes.TROOP, 'Gascony'),
    }

    helper = AdjustmentHelper(
        [
            PlayerHelper('France', [
                AdjustmentCommandHelper(AdjustmentCommandType.DISBAND, UnitTypes.TROOP, 'Paris'),
                AdjustmentCommandHelper(AdjustmentCommandType.DISBAND, UnitTypes.TROOP, 'Paris'),
            ]),
        ],
        player_units=player_units,
    )

    with pytest.raises(AssertionError):
        helper.resolve__validated()


def test_j_2b__removing_the_same_unit_twice__not_validated():
    # France has lost one territory to England and one to Germany, all other players have stayed still
    player_units = vanilla_dip.generate_starting_player_units()
    player_units['England'] = {
        Unit(UnitTypes.FLEET, 'English Channel'),
        Unit(UnitTypes.TROOP, 'Brest'),
        Unit(UnitTypes.TROOP, 'Edinburgh'),
    }
    player_units['Germany'] = {
        Unit(UnitTypes.FLEET, 'Kiel Coast'),
        Unit(UnitTypes.TROOP, 'Marseilles'),
        Unit(UnitTypes.TROOP, 'Berlin'),
    }
    player_units['France'] = {
        Unit(UnitTypes.FLEET, 'Mid-Atlantic Ocean'),
        Unit(UnitTypes.TROOP, 'Paris'),
        Unit(UnitTypes.TROOP, 'Gascony'),
    }

    helper = AdjustmentHelper(
        [
            PlayerHelper('France', [
                AdjustmentCommandHelper(AdjustmentCommandType.DISBAND, UnitTypes.TROOP, 'Paris'),
                AdjustmentCommandHelper(AdjustmentCommandType.DISBAND, UnitTypes.TROOP, 'Paris'),
            ]),
        ],
        player_units=player_units,
    )

    # Rather than using "distance", our Civil Disobedience rules will pick in alphabetical order
    results = helper.resolve()
    expected_results = deepcopy(player_units)
    expected_results['France'] = {
        Unit(UnitTypes.FLEET, 'Mid-Atlantic Ocean'),
    }
    assert results == expected_results


def test_j_3a__civil_disorder_two_armies_with_different_distance__validated():
    # Russia has lost a territory to Germany and a territory to Turkey, all other units stay put
    player_units = vanilla_dip.generate_starting_player_units()
    player_units['Russia'] = {
        Unit(UnitTypes.FLEET, 'St. Petersburg South Coast'),
        Unit(UnitTypes.TROOP, 'Prussia'),
        Unit(UnitTypes.TROOP, 'Ukraine'),
        Unit(UnitTypes.FLEET, 'Black Sea'),
    }
    player_units['Germany'] = {
        Unit(UnitTypes.FLEET, 'Kiel Coast'),
        Unit(UnitTypes.TROOP, 'Warsaw'),
        Unit(UnitTypes.TROOP, 'Munich'),
    }
    player_units['Turkey'] = {
        Unit(UnitTypes.FLEET, 'Sevastopol Coast'),
        Unit(UnitTypes.TROOP, 'Smyrna'),
        Unit(UnitTypes.TROOP, 'Constantinople'),
    }

    helper = AdjustmentHelper(
        [ ],
        player_units=player_units,
    )

    with pytest.raises(AssertionError):
        helper.resolve__validated()


def test_j_3b__civil_disorder_two_armies_with_different_distance__not_validated():
    # Russia has lost a territory to Germany and a territory to Turkey, all other units stay put
    player_units = vanilla_dip.generate_starting_player_units()
    player_units['Russia'] = {
        Unit(UnitTypes.FLEET, 'St. Petersburg South Coast'),
        Unit(UnitTypes.TROOP, 'Prussia'),
        Unit(UnitTypes.TROOP, 'Ukraine'),
        Unit(UnitTypes.FLEET, 'Black Sea'),
    }
    player_units['Germany'] = {
        Unit(UnitTypes.FLEET, 'Kiel Coast'),
        Unit(UnitTypes.TROOP, 'Warsaw'),
        Unit(UnitTypes.TROOP, 'Munich'),
    }
    player_units['Turkey'] = {
        Unit(UnitTypes.FLEET, 'Sevastopol Coast'),
        Unit(UnitTypes.TROOP, 'Smyrna'),
        Unit(UnitTypes.TROOP, 'Constantinople'),
    }

    helper = AdjustmentHelper(
        [],
        player_units=player_units,
    )

    # Rather than using "distance", our Civil Disobedience rules will pick in alphabetical order
    results = helper.resolve()
    expected_results = deepcopy(player_units)
    expected_results['Russia'] = {
        Unit(UnitTypes.FLEET, 'St. Petersburg South Coast'),
        Unit(UnitTypes.TROOP, 'Ukraine'),
    }
    assert results == expected_results


# Tests J.4-J.11 are skipped, since they are functionally equivalent to J.3 in our system
