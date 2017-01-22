from pydip.player.command.retreat_command import RetreatCommand, RetreatMoveCommand
from pydip.player.unit import Unit


def resolve_retreats(retreat_map, commands):
    """
    Returns resulting board state by considering interactions of provided list
    of retreat commands.

    retreat_map is intended to be the output from turn.resolve.resolve_turn.
    That is, a mapping of players to mappings of units to either None (in the
    case that a retreat is not expected for that unit), or a set of territory
    names (which hold the valid retreat targets).

    Returns a mapping of players to lists of units, representing which units
    in which locations those players will have after resolving retreats. Will
    be equivalent to the entries in retreat_map, minus any disbanded units --
    and, of course, without any retreat requirements.
    """
    assert all(isinstance(command, RetreatCommand) for command in commands)
    retreaters = { (command.player.name, command.unit) for command in commands }
    valid_retreaters = set()
    for player in retreat_map.keys():
        valid_retreaters |= {
            (player, unit)
            for unit in retreat_map[player].keys()
            if retreat_map[player][unit] is not None
        }
    assert retreaters == valid_retreaters

    result_map = { player : set() for player in retreat_map }
    for player in retreat_map:
        for unit in retreat_map[player]:
            if retreat_map[player][unit] is None:
                result_map[player].add(unit)

    commands = list(filter(lambda c: isinstance(c, RetreatMoveCommand), commands))
    for command in commands:
        other_commands = list(filter(lambda c: c != command, commands))
        if all(command.destination != other_command.destination for other_command in other_commands):
            result_map[command.player.name].add(Unit(command.unit.unit_type, command.destination))

    return result_map
