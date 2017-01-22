import pytest

from pydip.map.territory import LandTerritory, SeaTerritory, CoastTerritory


def test_coast_needs_land_parent():
    bad_parent = SeaTerritory('Black Sea')
    good_parent = LandTerritory('Sevastopol', ['Sevastopol Coast'])

    with pytest.raises(AssertionError):
        CoastTerritory('Test Fail Coast 1', bad_parent)

    with pytest.raises(AssertionError):
        CoastTerritory('Test Fail Coast 2', good_parent.coasts[0])

    """ expect this to create a coast without AssertionError """
    CoastTerritory('Test Success Coast', good_parent)
