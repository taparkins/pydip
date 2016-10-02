from data.map.territory import LandTerritory, SeaTerritory

class Map:
    """ String -> Territory """
    name_map = None

    """ String -> String{} (Adjacency List) """
    adjacency = None

    """
    territory_descriptors: list of structs defining new territories. Of the form:
        {
            'name': String,
            'coasts': [ { 'name': String } ] (Optional)
        }

        If 'coasts' is provided, the territory is Land, with Coasts as children. Otherwise it is Sea.

    adjacencies: list of tuples of names representing adjacent territories. Must be legal:
        * Sea adjacent only to Sea or Coast
        * Coast adjacent only to Sea or Coast
        * Land adjacent only to Land
        * All names must be provided in territory_descriptors
        * No duplicate adjacencies!
    """
    def __init__(self, territory_descriptors, adjacencies):
        self.name_map = dict()
        self.adjacency = dict()

        self._setup_name_map(territory_descriptors)
        self._setup_adjacencies(adjacencies)

    def _setup_name_map(self, territory_descriptors):
        for descriptor in territory_descriptors:
            assert 'name' in descriptor
            name = descriptor['name']
            if 'coasts' in descriptor:
                land = LandTerritory(name, descriptor['coasts'])
                self._add_territory(land)
                for coast in land.coasts:
                    self._add_territory(coast)
            else:
                self._add_territory(SeaTerritory(name))

    def _add_territory(self, territory):
        self.name_map[territory.name] = territory
        self.adjacency[territory.name] = set()

    def _setup_adjacencies(self, adjacencies):
        for name_a, name_b in adjacencies:
            assert name_a in self.name_map
            assert name_b in self.name_map

            territory_a = self.name_map[name_a]
            territory_b = self.name_map[name_b]

            assert ~(isinstance(territory_a, LandTerritory) ^ isinstance(territory_b, LandTerritory))
            assert name_b not in self.adjacency[name_a]
            assert name_a not in self.adjacency[name_b]

            self.adjacency[name_a].add(name_b)
            self.adjacency[name_b].add(name_a)