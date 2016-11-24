from player.command.command import MoveCommand, ConvoyMoveCommand
from turn.adjudicate.convoy import has_path
from turn.resolve import _resolve


def adjudicate_move(map, command_map, command):
    assert isinstance(command, MoveCommand) or isinstance(command, ConvoyMoveCommand)

    attack_strength = _attack_strength(map, command_map, command)

    prevent_combatants     = _get_prevent_combatants(command_map, command)
    high_prevent_strength = max([_prevent_strength(map, command_map, prevent_combatant)
                                 for prevent_combatant in prevent_combatants])
    if attack_strength <= high_prevent_strength:
        return False

    head_to_head_combatant = _get_head_to_head_combatant(command_map, command)
    if head_to_head_combatant is not None:
        return attack_strength > _defend_strength(map, command_map, head_to_head_combatant)
    return attack_strength > _hold_strength(map, command_map, command.destination)

def _get_prevent_combatants(command_map, command):
    direct_combatants = command_map.get_attackers(command.destination)
    convoy_combatants = command_map.get_convoy_attackers(command.destination)
    combatants = direct_combatants + convoy_combatants
    combatants = filter(lambda c: c != command, combatants)
    return combatants

def _get_head_to_head_combatant(command_map, command):
    potential_attacker = command_map.get_home_command(command.destination)
    if potential_attacker is not None:
        if isinstance(potential_attacker, MoveCommand) or isinstance(potential_attacker, ConvoyMoveCommand):
            if potential_attacker.destination == command.unit.position:
                return potential_attacker
    return None

def _attack_strength(map, command_map, command):
    if isinstance(command, ConvoyMoveCommand):
        if not has_path(map, command_map, command):
            return 0
    attacked_command = command_map.get_home_command(command.destination)
    supporters = command_map.get_supports(command.unit.position, command.destination)
    supporters = filter(lambda c: _resolve(map, command_map, c), supporters)

    if attacked_command is not None:
        if attacked_command.player.name == command.player.name:
            return 0
        if isinstance(attacked_command, MoveCommand) or isinstance(attacked_command, ConvoyMoveCommand):
            if not _resolve(map, command_map, attacked_command):
                supporters = filter(lambda c: c.player.name != attacked_command.player.name, supporters)
        else:
            supporters = filter(lambda c: c.player.name != attacked_command.player.name, supporters)

    return 1 + len(list(supporters))

def _prevent_strength(map, command_map, command):
    if isinstance(command, ConvoyMoveCommand):
        if not has_path(map, command_map, command):
            return 0
    head_to_head_combatant = _get_head_to_head_combatant(command_map, command)
    if head_to_head_combatant is not None:
        if _resolve(map, command_map, head_to_head_combatant):
            return 0

    supporters = command_map.get_supports(command.unit.position, command.destination)
    supporters = filter(lambda c: _resolve(map, command_map, c), supporters)
    return 1 + len(list(supporters))

def _defend_strength(map, command_map, command):
    supporters = command_map.get_supports(command.unit.position, command.destination)
    supporters = filter(lambda c: _resolve(map, command_map, c), supporters)
    return 1 + len(list(supporters))

def _hold_strength(map, command_map, territory):
    home_command = command_map.get_home_command(territory)
    if home_command is None:
        return 0
    if isinstance(home_command, MoveCommand) or isinstance(home_command, ConvoyMoveCommand):
        return 0 if _resolve(map, command_map, home_command) else 1
    supporters = command_map.get_supports(territory, territory)
    supporters = filter(lambda c: _resolve(map, command_map, c), supporters)
    return 1 + len(list(supporters))