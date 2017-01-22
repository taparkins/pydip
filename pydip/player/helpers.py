from pydip.map.territory import CoastTerritory, SeaTerritory, LandTerritory
from pydip.player.unit import UnitTypes


def unit_can_enter(game_map, unit, territory):
    if territory.name not in game_map.adjacency[unit.position]:
        return False
    else:
        return unit_type_can_enter(unit.unit_type, territory)


def unit_type_can_enter(unit_type, territory):
    if unit_type == UnitTypes.TROOP:
        return isinstance(territory, LandTerritory)
    elif unit_type == UnitTypes.FLEET:
        return isinstance(territory, SeaTerritory) or isinstance(territory, CoastTerritory)
    else:
        raise ValueError("Invalid UnitType: {}".format(unit_type))


def unit_can_support(game_map, unit, territory):
    """
    Being able to enter a coast or a land territory allows you to support,
    so we'll check each possible option
    """
    territories_to_check = [ territory ]
    if isinstance(territory, LandTerritory):
        territories_to_check.extend(territory.coasts)
    elif isinstance(territory, CoastTerritory):
        territories_to_check.append(territory.parent)
        territories_to_check.extend(territory.parent.coasts)

    return any(unit_can_enter(game_map, unit, to_check) for to_check in territories_to_check)


def territory_is_convoy_compatible(territory):
    return isinstance(territory, LandTerritory) and len(territory.coasts) > 0
