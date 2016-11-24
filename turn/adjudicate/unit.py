from player.command.command import ConvoyMoveCommand, MoveCommand
from turn.resolve import _resolve


def is_dislodged(map, command_map, unit):
    return any((_resolve(map, command_map, attack) for attack in _attackers(command_map, unit)))

def _attackers(command_map, unit):
    filtered = command_map.values()
    filtered = filter(lambda c: isinstance(c, MoveCommand) or isinstance(c, ConvoyMoveCommand), filtered)
    filtered = filter(lambda c: c.destination == unit.position, filtered)

    return list(filtered)