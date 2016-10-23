from map.territory import CoastTerritory
from player.command.command import ConvoyTransportCommand, ConvoyMoveCommand

"""
Given a ConvoyMoveCommand, searches all ConvoyTransportCommands to see if
a possible transport chain exists.

map: Map representing current game board
move_command: ConvoyMoveCommand to check for existing convoy transport chain
commands: Command[] representing all commands in the turn

Returns true if there is a possible transport chain of synchronized transport
commands that agree with move_command. False if no such chain exists.
"""
def convoy_chain_exists(map, move_command, commands):
    assert isinstance(move_command, ConvoyMoveCommand)
    visited = set()
    transport_map = _get_transport_map(move_command, commands)

    starting_territory = map.name_map[move_command.unit.position]
    destination = move_command.destination
    coastal_adjacencies = [map.adjacency[coast.name] for coast in starting_territory.coasts]
    to_visit = [
        territory for territory in transport_map.keys()
        if any(territory in coastal_adjacency for coastal_adjacency in coastal_adjacencies)
    ]

    while len(to_visit) > 0:
        visiting = to_visit.pop()
        visited.add(visiting)
        adjacent = [map.name_map[adj] for adj in map.adjacency[visiting]]

        adjacent_land = {
            coast.parent.name for coast in adjacent
            if isinstance(coast, CoastTerritory)
        }
        if destination in adjacent_land:
            return True

        to_visit = [
            territory.name for territory in adjacent
            if (territory.name not in visited and
                territory.name in transport_map)
        ] + to_visit

    return False

def _get_transport_map(move_command, commands):
    map = dict()
    for command in commands:
        if isinstance(command, ConvoyTransportCommand):
            if (command.transported_unit == move_command.unit and
                command.destination == move_command.destination):
                map[command.unit.position] = command
    return map