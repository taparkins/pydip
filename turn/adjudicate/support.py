from player.command.command import SupportCommand, ConvoyMoveCommand, MoveCommand
from turn.adjudicate.convoy import has_path
from turn.adjudicate.unit import is_dislodged


def adjudicate_support(map, command_map, command):
    assert isinstance(command, SupportCommand)
    if _invalid_support(command_map, command):
        return False
    if len(_indirect_non_convoy_attackers(command_map, command)) > 0:
        return False
    for convoy_attacker in _indirect_convoy_attackers(command_map, command.unit.position):
        if has_path(map, command_map, convoy_attacker):
            return False
    return is_dislodged(map, command_map, command.unit)

def _invalid_support(command_map, command):
    supported_command = command_map.get_home_command(command.supported_unit.position)
    if isinstance(supported_command, MoveCommand) or isinstance(supported_command, ConvoyMoveCommand):
        return supported_command.destination != command.destination
    return command.destination != command.supported_unit.position

def _indirect_non_convoy_attackers(command_map, command):
    filtered = command_map.get_attackers(command.unit.position)
    filtered = filter(lambda c: c.unit.position != command.destination, filtered)
    filtered = filter(lambda c: c.player != command.player, filtered)
    return list(filtered)

def _indirect_convoy_attackers(command_map, command):
    filtered = command_map.get_convoy_attackers(command.unit.position)
    filtered = filter(lambda c: c.unit.position != command.destination, filtered)
    filtered = filter(lambda c: c.player.name != command.player.name, filtered)
    return list(filtered)
