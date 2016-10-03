from player.unit import Unit, UnitTypes
from map.territory import SeaTerritory, CoastTerritory, LandTerritory

class Player:
    """ String -- name identifier for player """
    name = None

    """ Map -- reference to game board """
    map = None

    """ Unit[] -- units owned by this player """
    units = None

    """ String{} -- names of starting territories for player """
    starting_territories = None

    """
     * name: String -- identifier for player
     * map:  Map    -- reference to game board
     * starting_configuration: Defines how player should begin configuration. List of structs of form:
        { 'territory_name': String, 'unit_type': UnitType? (None indicates no unit) }
        - Duplicate territory definitions are not allowed!
        - Coasts should be provided as starting territories for fleets, but the parent will be labeled as the actual
          starting territory.
    """
    def __init__(self, name, map, starting_configuration):
        self.name = name
        self.map = map
        self.starting_territories = set()
        self.units = []

        for config in starting_configuration:
            name = config['territory_name']
            unit_type = config['unit_type']
            assert name in self.map.name_map.keys()

            territory = self.map.name_map[name]
            starting_territory = territory.parent if isinstance(territory, CoastTerritory) else territory
            assert starting_territory.name in self.map.name_map.keys()
            assert starting_territory.name not in self.starting_territories
            self.starting_territories.add(starting_territory.name)

            if unit_type is None:
                continue
            elif unit_type == UnitTypes.FLEET:
                assert isinstance(territory, CoastTerritory) or isinstance(territory, SeaTerritory)
            elif unit_type == UnitTypes.TROOP:
                assert isinstance(territory, LandTerritory)
            else:
                raise ValueError("Invalid UnitType: {}".format(unit_type))

            self.units.append(Unit(unit_type, name))

        assert len(self.starting_territories) == len(starting_configuration)