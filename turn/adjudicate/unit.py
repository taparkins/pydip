from player.command.command import ConvoyMoveCommand, MoveCommand
from turn.resolve import _resolve

"""
Determines if the unit will be dislodged by a different move, assuming it stays in place.
Please note that this function does not indicate whether the unit _will_ stay in place.
"""
def is_dislodged(map, command_map, unit):
    return any((_resolve(map, command_map, attack) for attack in _attackers(command_map, unit)))

def _attackers(command_map, unit):
    filtered = command_map.values()
    filtered = filter(lambda c: isinstance(c, MoveCommand) or isinstance(c, ConvoyMoveCommand), filtered)
    filtered = filter(lambda c: c.destination == unit.position, filtered)

    return list(filtered)