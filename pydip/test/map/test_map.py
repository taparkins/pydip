from pydip.map.territory import SeaTerritory, LandTerritory
from pydip.map.map import Map


def test_empty_map():
    territory_descriptors = []
    adjacencies = []

    game_map = Map(territory_descriptors, adjacencies)
    expected_name_map = dict()
    expected_adjacency = dict()

    assert game_map.name_map == expected_name_map
    assert game_map.adjacency == expected_adjacency


def test_singleton_map():
    territory_descriptors = [ { 'name' : 'Pacific Ocean' } ]
    adjacencies = []

    game_map = Map(territory_descriptors, adjacencies)
    expected_name_map = { 'Pacific Ocean' : SeaTerritory('Pacific Ocean') }
    expected_adjacency = { 'Pacific Ocean' : set() }

    assert game_map.name_map == expected_name_map
    assert game_map.adjacency == expected_adjacency


def test_two_connected_land_territories():
    territory_descriptors = [
        { 'name' : 'United States', 'coasts' : [] },
        { 'name' : 'Mexico',        'coasts' : [] },
    ]
    adjacencies = [ ('United States', 'Mexico' ) ]

    game_map = Map(territory_descriptors, adjacencies)
    expected_name_map = {
        'United States' : LandTerritory('United States', []),
        'Mexico'        : LandTerritory('Mexico',        []),
    }
    expected_adjacency = {
        'United States' : { 'Mexico' },
        'Mexico'        : { 'United States' },
    }

    assert game_map.name_map == expected_name_map
    assert game_map.adjacency == expected_adjacency


def test_land_territories_with_lake():
    territory_descriptors = [
        { 'name': 'Salt Lake City', 'coasts': [ 'Salt Lake City Coast' ] },
        { 'name': 'Ogden',          'coasts': [ 'Ogden Coast' ] },
        { 'name': 'Great Salt Lake' },
    ]
    adjacencies = [
        ('Salt Lake City', 'Ogden'),
        ('Salt Lake City Coast', 'Great Salt Lake'),
        ('Salt Lake City Coast', 'Ogden Coast'),
        ('Ogden Coast', 'Great Salt Lake'),
    ]

    game_map = Map(territory_descriptors, adjacencies)
    slc_territory = LandTerritory('Salt Lake City', ['Salt Lake City Coast'])
    ogden_territory = LandTerritory('Ogden', ['Ogden Coast'])
    expected_name_map = {
        'Salt Lake City': slc_territory,
        'Salt Lake City Coast': slc_territory.coasts[0],
        'Ogden': ogden_territory,
        'Ogden Coast': ogden_territory.coasts[0],
        'Great Salt Lake': SeaTerritory('Great Salt Lake')
    }
    expected_adjacency = {
        'Salt Lake City'      : {'Ogden'},
        'Salt Lake City Coast': {'Ogden Coast', 'Great Salt Lake'},
        'Ogden'               : {'Salt Lake City'},
        'Ogden Coast'         : {'Salt Lake City Coast', 'Great Salt Lake'},
        'Great Salt Lake'     : {'Salt Lake City Coast', 'Ogden Coast'}
    }

    assert game_map.name_map == expected_name_map
    assert game_map.adjacency == expected_adjacency
