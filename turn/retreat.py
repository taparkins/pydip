from collections import defaultdict

from map.territory import LandTerritory, CoastTerritory
from player.command.command import ConvoyMoveCommand, MoveCommand
from player.unit import Unit


def compute_retreats(map, command_map, commands, resolutions):
    player_results = defaultdict(dict)
    occupied_territories = _get_occupations(map, command_map, commands, resolutions)

    for command in commands:
        current_position = command.unit.position
        if resolutions[current_position]:
            if isinstance(command, MoveCommand) or isinstance(command, ConvoyMoveCommand):
                moved_unit = Unit(command.unit.unit_type, command.destination)
                player_results[command.player.name][moved_unit] = None
            else:
                player_results[command.player.name][command.unit] = None
        else:
            attackers = command_map.get_attackers(current_position) + command_map.get_convoy_attackers(current_position)
            attackers = list(filter(lambda c: resolutions[c.unit.position], attackers))
            if len(attackers) == 0:
                player_results[command.player.name][command.unit] = None
            else:
                retreat_options = map.adjacency[current_position]
                retreat_options = filter(lambda t: t not in occupied_territories, retreat_options)
                retreat_options = filter(lambda t: all(t not in _applicable_territories(map, attacker.unit.position) for attacker in attackers), retreat_options)
                retreat_options = filter(lambda t: not _attacked_by_other_unit(command_map, command, t), retreat_options)

                player_results[command.player.name][command.unit] = set(retreat_options)

    return player_results

def _applicable_territories(map, territory_name):
    territory = map.name_map[territory_name]
    applicable = { territory_name }
    if isinstance(territory, LandTerritory):
        applicable |= { coast.name for coast in territory.coasts }
    elif isinstance(territory, CoastTerritory):
        applicable.add(territory.parent.name)
        applicable |= { coast.name for coast in territory.parent.coasts }

    return applicable

def _get_occupations(map, command_map, commands, resolutions):
    occupations = set()
    for command in commands:
        if isinstance(command, MoveCommand) or isinstance(command, ConvoyMoveCommand):
            if resolutions[command.unit.position]:
                occupations |= _applicable_territories(map, command.destination)
            else:
                occupations |= _applicable_territories(map, command.unit.position)
        else:
            occupations |= _applicable_territories(map, command.unit.position)

    return occupations

def _attacked_by_other_unit(command_map, command, territory):
    attackers = command_map.get_attackers(territory) + command_map.get_convoy_attackers(territory)
    attackers = filter(lambda c: c != command, attackers)
    return len(list(attackers)) > 0