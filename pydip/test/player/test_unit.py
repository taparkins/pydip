from pydip.player.unit import UnitTypes, Unit


def test_same_position_and_type_are_equal():
    unit_a = Unit(UnitTypes.FLEET, 'Adriatic Sea')
    unit_b = Unit(UnitTypes.FLEET, 'Adriatic Sea')

    assert unit_a == unit_b
    assert not unit_a != unit_b


def test_different_position_same_type_are_not_equal():
    unit_a = Unit(UnitTypes.TROOP, 'Trieste')
    unit_b = Unit(UnitTypes.TROOP, 'Constantinople')

    assert not unit_a == unit_b
    assert unit_a != unit_b


def test_same_position_different_type_are_not_equal():
    unit_a = Unit(UnitTypes.FLEET, 'Constantinople')
    unit_b = Unit(UnitTypes.TROOP, 'Constantinople')

    assert not unit_a == unit_b
    assert unit_a != unit_b


def test_different_position_and_type_are_not_equal():
    unit_a = Unit(UnitTypes.FLEET, 'Finland Coast')
    unit_b = Unit(UnitTypes.TROOP, 'Constantinople')

    assert not unit_a == unit_b
    assert unit_a != unit_b
