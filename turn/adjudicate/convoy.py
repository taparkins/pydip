from map.territory import SeaTerritory, CoastTerritory
from player.command.command import ConvoyMoveCommand, ConvoyTransportCommand
from turn.adjudicate.move import adjudicate_move
from turn.adjudicate.unit import is_dislodged
from turn.resolve import _resolve


def adjudicate_convoy_move(map, command_map, command):
    assert isinstance(command, ConvoyMoveCommand)
    if not has_path(map, command_map, command):
        return False
    return adjudicate_move(map, command_map, command)

def adjudicate_convoy_transport(map, command_map, command):
    assert isinstance(command, ConvoyTransportCommand)
    return not is_dislodged(map, command_map, command.unit)

def has_path(map, command_map, command):
    assert isinstance(command, ConvoyMoveCommand)
    visited     = set()
    source      = command.unit.position
    destination = command.destination
    possible_transports = command_map.get_transport_commands[(source, destination)]
    possible_transport_territories = { transport.unit.position for transport in possible_transports }

    starting_territory = map.name_map[source]
    coastal_adjacencies = [map.adjacency[coast.name] for coast in starting_territory.coasts]
    coastal_adjacencies = filter(lambda t: isinstance(t, SeaTerritory), coastal_adjacencies)
    to_visit = [
        possible_transport_territory
        for possible_transport_territory in possible_transport_territories
        if any(possible_transport_territory in coastal_adjacency for coastal_adjacency in coastal_adjacencies)
    ]

    while len(to_visit) > 0:
        visiting = to_visit.pop()
        visited.add(visiting)
        # if the convoy was disrupted, we can't use it as part of our chain
        if not _resolve(map, command_map, command_map.get_home_command(visiting)):
            continue

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
               territory.name in possible_transport_territories)
        ] + to_visit

    return False