from pydip.player.unit import Unit
from pydip.player.helpers import unit_type_can_enter
from pydip.map.territory import CoastTerritory


class Player:
    """ String -- name identifier for player """
    name = None

    """ Map -- reference to game board """
    game_map = None

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
    def __init__(self, name, game_map, starting_configuration):
        self.name = name
        self.game_map = game_map
        self.starting_territories = set()
        self.units = []

        for config in starting_configuration:
            name = config['territory_name']
            unit_type = config['unit_type']
            assert name in self.game_map.name_map.keys()

            territory = self.game_map.name_map[name]
            starting_territory = territory.parent if isinstance(territory, CoastTerritory) else territory
            assert starting_territory.name in self.game_map.name_map.keys()
            assert starting_territory.name not in self.starting_territories
            self.starting_territories.add(starting_territory.name)

            if unit_type is None:
                continue
            assert unit_type_can_enter(unit_type, territory)

            self.units.append(Unit(unit_type, name))

        assert len(self.starting_territories) == len(starting_configuration)
