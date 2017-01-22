import pytest

from pydip.map.predefined import vanilla_dip
from pydip.player.unit import Unit
from pydip.player.unit import UnitTypes
from pydip.test.adjustment_helper import AdjustmentHelper
from pydip.test.command_helper import AdjustmentCommandHelper, AdjustmentCommandType
from pydip.test.player_helper import PlayerHelper


def test_i_1a__too_many_build_orders__with_validation():
    """
    This test has been modified from the DATC -- it includes a build from a non-home territory, which
    fails for a completely separate reason, before we even reach order resolution.
    """

    # Germany has captured one new territory, all other players have stayed still
    player_units = vanilla_dip.generate_starting_player_units()
    player_units['Germany'] = {
        Unit(UnitTypes.FLEET, 'Holland Coast'),
        Unit(UnitTypes.TROOP, 'Prussia'),
        Unit(UnitTypes.TROOP, 'Tyrolia'),
    }

    helper = AdjustmentHelper(
        [
            PlayerHelper('Germany', [
                AdjustmentCommandHelper(AdjustmentCommandType.CREATE, UnitTypes.TROOP, 'Berlin'),
                AdjustmentCommandHelper(AdjustmentCommandType.CREATE, UnitTypes.TROOP, 'Kiel'),
                AdjustmentCommandHelper(AdjustmentCommandType.CREATE, UnitTypes.TROOP, 'Munich'),
            ]),
        ],
        player_units=player_units,
    )

    with pytest.raises(AssertionError):
        helper.resolve__validated()


def test_i_1b__too_many_build_orders():
    """
    This test has been modified from the DATC -- it includes a build from a non-home territory, which
    fails for a completely separate reason, before we even reach order resolution.
    """

    # Germany has captured one new territory, all other players have stayed still
    player_units = vanilla_dip.generate_starting_player_units()
    player_units['Germany'] = {
        Unit(UnitTypes.FLEET, 'Holland Coast'),
        Unit(UnitTypes.TROOP, 'Prussia'),
        Unit(UnitTypes.TROOP, 'Tyrolia'),
    }

    helper = AdjustmentHelper(
        [
            PlayerHelper('Germany', [
                AdjustmentCommandHelper(AdjustmentCommandType.CREATE, UnitTypes.TROOP, 'Berlin'),
                AdjustmentCommandHelper(AdjustmentCommandType.CREATE, UnitTypes.TROOP, 'Kiel'),
                AdjustmentCommandHelper(AdjustmentCommandType.CREATE, UnitTypes.TROOP, 'Munich'),
            ]),
        ],
        player_units=player_units,
    )

    # prioritize first-issued command
    results = helper.resolve()
    expected_results = vanilla_dip.generate_starting_player_units()
    expected_results['Germany'] = {
        Unit(UnitTypes.FLEET, 'Holland Coast'),
        Unit(UnitTypes.TROOP, 'Prussia'),
        Unit(UnitTypes.TROOP, 'Tyrolia'),
        Unit(UnitTypes.TROOP, 'Berlin'),
    }
    assert results == expected_results


def test_i_2__fleets_cannot_be_built_in_land_areas():
    # Russia has captured one new territory, all other players have stayed still
    player_units = vanilla_dip.generate_starting_player_units()
    player_units['Russia'] = {
        Unit(UnitTypes.FLEET, 'Sweden Coast'),
        Unit(UnitTypes.TROOP, 'Prussia'),
        Unit(UnitTypes.TROOP, 'Galicia'),
        Unit(UnitTypes.FLEET, 'Black Sea'),
    }

    with pytest.raises(AssertionError):
        AdjustmentHelper(
            [
                PlayerHelper('Russia', [
                    AdjustmentCommandHelper(AdjustmentCommandType.CREATE, UnitTypes.FLEET, 'Moscow'),
                ]),
            ],
            player_units=player_units,
        )


def test_i_3__supply_center_must_be_empty_for_building():
    # Germany has captured one new territory, all other players have stayed still
    player_units = vanilla_dip.generate_starting_player_units()
    player_units['Germany'] = {
        Unit(UnitTypes.FLEET, 'Holland Coast'),
        Unit(UnitTypes.TROOP, 'Berlin'),
        Unit(UnitTypes.TROOP, 'Tyrolia'),
    }

    with pytest.raises(AssertionError):
        AdjustmentHelper(
            [
                PlayerHelper('Germany', [
                    AdjustmentCommandHelper(AdjustmentCommandType.CREATE, UnitTypes.TROOP, 'Berlin'),
                ]),
            ],
            player_units=player_units,
        )


def test_i_4__both_coasts_must_be_empty_for_building():
    # Russia has captured one new territory, all other players have stayed still
    player_units = vanilla_dip.generate_starting_player_units()
    player_units['Russia'] = {
        Unit(UnitTypes.FLEET, 'St. Petersburg South Coast'),
        Unit(UnitTypes.TROOP, 'Prussia'),
        Unit(UnitTypes.TROOP, 'Galicia'),
        Unit(UnitTypes.FLEET, 'Rumania Coast'),
    }

    with pytest.raises(AssertionError):
        AdjustmentHelper(
            [
                PlayerHelper('Russia', [
                    AdjustmentCommandHelper(
                        AdjustmentCommandType.CREATE,
                        UnitTypes.FLEET,
                        'St. Petersburg North Coast',
                    ),
                ]),
            ],
            player_units=player_units,
        )


def test_i_5__building_in_home_supply_center_that_is_not_owned():
    # Russia has captured Berlin, and moved out, and Germany will be capturing Holland
    player_units = vanilla_dip.generate_starting_player_units()
    player_units['Germany'] = {
        Unit(UnitTypes.FLEET, 'Kiel Coast'),
        Unit(UnitTypes.TROOP, 'Holland'),
    }
    player_units['Russia'] = {
        Unit(UnitTypes.FLEET, 'St. Petersburg South Coast'),
        Unit(UnitTypes.TROOP, 'Moscow'),
        Unit(UnitTypes.FLEET, 'Sevastopol Coast'),
        Unit(UnitTypes.TROOP, 'Prussia'),
        Unit(UnitTypes.TROOP, 'Warsaw'),
    }

    owned_territories = vanilla_dip.generate_home_territories()
    owned_territories['Germany'] = { 'Kiel', 'Munich' }
    owned_territories['Russia'] = { 'St. Petersburg', 'Sevastopol', 'Moscow', 'Berlin', 'Warsaw' }

    with pytest.raises(AssertionError):
        AdjustmentHelper(
            [
                PlayerHelper('Germany', [
                    AdjustmentCommandHelper(AdjustmentCommandType.CREATE, UnitTypes.TROOP, 'Berlin'),
                ]),
            ],
            player_units=player_units,
            owned_territories=owned_territories,
        )


def test_i_6__building_in_owned_supply_center_that_is_not_a_home_supply_center():
    # Germany has captured Warsaw, and moved out
    player_units = vanilla_dip.generate_starting_player_units()
    player_units['Germany'] = {
        Unit(UnitTypes.FLEET, 'Kiel Coast'),
        Unit(UnitTypes.TROOP, 'Munich'),
        Unit(UnitTypes.TROOP, 'Ukraine'),
        Unit(UnitTypes.TROOP, 'Berlin'),
    }
    player_units['Russia'] = {
        Unit(UnitTypes.FLEET, 'St. Petersburg South Coast'),
        Unit(UnitTypes.TROOP, 'Moscow'),
        Unit(UnitTypes.FLEET, 'Sevastopol Coast'),
    }

    owned_territories = vanilla_dip.generate_home_territories()
    owned_territories['Germany'] = { 'Kiel', 'Munich', 'Berlin', 'Warsaw' }
    owned_territories['Russia'] = { 'St. Petersburg', 'Sevastopol', 'Moscow' }

    with pytest.raises(AssertionError):
        AdjustmentHelper(
            [
                PlayerHelper('Germany', [
                    AdjustmentCommandHelper(AdjustmentCommandType.CREATE, UnitTypes.TROOP, 'Warsaw'),
                ]),
            ],
            player_units=player_units,
            owned_territories=owned_territories,
        )


def test_i_7a__only_one_build_in_a_home_supply_center__validated():
    # Russia has captured two territories, everyone else has stayed put
    player_units = vanilla_dip.generate_starting_player_units()
    player_units['Russia'] = {
        Unit(UnitTypes.FLEET, 'Sweden Coast'),
        Unit(UnitTypes.TROOP, 'Warsaw'),
        Unit(UnitTypes.TROOP, 'Ukraine'),
        Unit(UnitTypes.FLEET, 'Rumania Coast'),
    }

    helper = AdjustmentHelper(
        [
            PlayerHelper('Russia', [
                AdjustmentCommandHelper(AdjustmentCommandType.CREATE, UnitTypes.TROOP, 'Moscow'),
                AdjustmentCommandHelper(AdjustmentCommandType.CREATE, UnitTypes.TROOP, 'Moscow'),
            ]),
        ],
        player_units=player_units,
    )

    with pytest.raises(AssertionError):
        helper.resolve__validated()


def test_i_7b__only_one_build_in_a_home_supply_center__not_validated():
    # Russia has captured two territories, everyone else has stayed put
    player_units = vanilla_dip.generate_starting_player_units()
    player_units['Russia'] = {
        Unit(UnitTypes.FLEET, 'Sweden Coast'),
        Unit(UnitTypes.TROOP, 'Warsaw'),
        Unit(UnitTypes.TROOP, 'Ukraine'),
        Unit(UnitTypes.FLEET, 'Rumania Coast'),
    }

    helper = AdjustmentHelper(
        [
            PlayerHelper('Russia', [
                AdjustmentCommandHelper(AdjustmentCommandType.CREATE, UnitTypes.TROOP, 'Moscow'),
                AdjustmentCommandHelper(AdjustmentCommandType.CREATE, UnitTypes.TROOP, 'Moscow'),
            ]),
        ],
        player_units=player_units,
    )

    results = helper.resolve()
    expected_results = vanilla_dip.generate_starting_player_units()
    expected_results['Russia'] = {
        Unit(UnitTypes.FLEET, 'Sweden Coast'),
        Unit(UnitTypes.TROOP, 'Warsaw'),
        Unit(UnitTypes.TROOP, 'Ukraine'),
        Unit(UnitTypes.FLEET, 'Rumania Coast'),
        Unit(UnitTypes.TROOP, 'Moscow'),
    }
    assert results == expected_results
