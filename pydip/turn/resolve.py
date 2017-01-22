from collections import defaultdict
from enum import Enum
from functools import reduce

from pydip.map.territory import CoastTerritory, SeaTerritory, LandTerritory
from pydip.player.command.command import MoveCommand, ConvoyMoveCommand, ConvoyTransportCommand, SupportCommand
from pydip.player.unit import Unit
from pydip.turn.command_map import CommandMap


def resolve_turn(game_map, commands):
    """
    Returns resulting positions of each unit by considering interactions
    of provided list of commands.

    Note: assumes that every unit on the map has been issued a command.
    If a unit has _not_ been issued a command, you ought to insert a
    HoldCommand for that unit by default.

    map: Map representing game board
    commands: Command[] representing each command issued for this turn
              Expected to be fully populated for each unit on the board
              (Recommended to default to Hold for units not given orders)

    returns a map of Player names to sub-maps representing results of that
    player's units. The sub-maps will be maps of Units to an optional set
    of territories, representing which territories the unit can retreat to.
    If the territory set is not provided, no retreat is required. If the
    territory set is provided, a retreat is required. If it is empty, no
    retreat is possible.
    """
    command_map = CommandMap(game_map, commands)
    _init_resolution()
    resolutions = {command.unit.position: _resolve(game_map, command_map, command) for command in commands}
    return compute_retreats(game_map, command_map, commands, resolutions)


#------------------------------------------------------------------------------
# Below implementation is taken with minor modification from Lucas Kruijswijk:
# http://www.diplom.org/Zine/S2009M/Kruijswijk/DipMath_Chp6.htm
#------------------------------------------------------------------------------


class ResolutionState(Enum):
    UNRESOLVED = 0
    GUESSING   = 1
    RESOLVED   = 2

resolution_map  = None
state_map       = None
dependency_list = None


def _init_resolution():
    global resolution_map
    global state_map
    global dependency_list
    resolution_map = defaultdict(bool)
    state_map      = defaultdict(lambda: ResolutionState.UNRESOLVED)
    dependency_list = list()


def _resolve(game_map, command_map, command):
    global resolution_map
    global state_map
    global dependency_list
    command_territory = command.unit.position

    if state_map[command_territory] == ResolutionState.RESOLVED:
        return resolution_map[command_territory]

    if state_map[command_territory] == ResolutionState.GUESSING:
        if command_territory not in dependency_list:
            dependency_list.append(command_territory)
        return resolution_map[command_territory]

    old_dependency_length = len(dependency_list)

    # Initially, guess that we fail
    resolution_map[command_territory] = False
    state_map[command_territory]      = ResolutionState.GUESSING
    fail_guess_result                 = _adjudicate(game_map, command_map, command)

    # If the dependency graph didn't change as a consequence, our result doesn't
    # depend on the guess and we can return right away
    if old_dependency_length == len(dependency_list):
        # This is possible because of the backup rule in paradox resolutions
        if state_map[command_territory] != ResolutionState.RESOLVED:
            resolution_map[command_territory] = fail_guess_result
            state_map[command_territory]      = ResolutionState.RESOLVED

        return fail_guess_result

    dependency_sub_set = set(dependency_list[old_dependency_length:])
    # If we don't depend on ourselves yet, we add ourselves in to complete the
    # cycle, and let our caller sort out the details
    if command_territory not in dependency_sub_set:
        dependency_list.append(command_territory)
        resolution_map[command_territory] = fail_guess_result
        return fail_guess_result

    # Otherwise, we depend on our own guess, so we need to clear out dependencies
    # to check the other guess for consistency
    for dependent_territory in dependency_sub_set:
        state_map[dependent_territory] = ResolutionState.UNRESOLVED
    dependency_list = dependency_list[:old_dependency_length]

    resolution_map[command_territory] = True
    state_map[command_territory]      = ResolutionState.GUESSING
    success_guess_result              = _adjudicate(game_map, command_map, command)

    # If results are consistent, no need for further checking
    if fail_guess_result == success_guess_result:
        for dependent_territory in dependency_sub_set:
            state_map[dependent_territory] = ResolutionState.UNRESOLVED
        dependency_list = dependency_list[:old_dependency_length]

        resolution_map[command_territory] = fail_guess_result
        state_map[command_territory]      = ResolutionState.RESOLVED
        return fail_guess_result

    # If we got to this point, that means we encountered a paradox that has two
    # consistent outcomes, and we need a backup rule to fully resolve it
    _backup_rule(command_map, dependency_sub_set)
    dependency_list = dependency_list[:old_dependency_length]

    # And because the backup rule may not resolve our own command, we'll need to
    # start fresh just to be sure
    return _resolve(game_map, command_map, command)


def _adjudicate(game_map, command_map, command):
    if isinstance(command, MoveCommand):
        return _adjudicate_move(game_map, command_map, command)
    elif isinstance(command, ConvoyMoveCommand):
        return _adjudicate_convoy_move(game_map, command_map, command)
    elif isinstance(command, ConvoyTransportCommand):
        return _adjudicate_convoy_transport(game_map, command_map, command)
    elif isinstance(command, SupportCommand):
        return _adjudicate_support(game_map, command_map, command)
    else:
        raise ValueError("Command unexpected type")


def _backup_rule(command_map, dependency_set):
    global resolution_map
    global state_map
    for dependency_territory in dependency_set:
        dependency = command_map.get_home_command(dependency_territory)
        if isinstance(dependency, MoveCommand):
            if isinstance(command_map.get_home_command(dependency.destination), ConvoyTransportCommand):
                _apply_szykman(command_map, dependency_set)
                return
    _apply_circular_movement(command_map, dependency_set)


def _apply_szykman(command_map, dependency_set):
    for dependency_territory in dependency_set:
        dependency = command_map.get_home_command(dependency_territory)
        if isinstance(dependency, ConvoyMoveCommand) or isinstance(dependency, ConvoyTransportCommand):
            resolution_map[dependency_territory] = False
            state_map[dependency_territory] = ResolutionState.RESOLVED
        else:
            state_map[dependency_territory] = ResolutionState.UNRESOLVED


def _apply_circular_movement(command_map, dependency_set):
    for dependency_territory in dependency_set:
        dependency = command_map.get_home_command(dependency_territory)
        if isinstance(dependency, MoveCommand) or isinstance(dependency, ConvoyMoveCommand):
            resolution_map[dependency_territory] = True
            state_map[dependency_territory] = ResolutionState.RESOLVED
        else:
            state_map[dependency_territory] = ResolutionState.UNRESOLVED


#----------------------
# convoys
#----------------------
def _adjudicate_convoy_move(game_map, command_map, command):
    assert isinstance(command, ConvoyMoveCommand)
    if not _has_path(game_map, command_map, command):
        return False
    return _adjudicate_move(game_map, command_map, command)


def _adjudicate_convoy_transport(game_map, command_map, command):
    assert isinstance(command, ConvoyTransportCommand)
    return not _is_dislodged(game_map, command_map, command.unit)


def _has_path(game_map, command_map, command):
    assert isinstance(command, ConvoyMoveCommand)
    visited     = set()
    source      = command.unit.position
    destination = command.destination
    possible_transports = command_map.get_convoy_transports(source, destination)
    possible_transport_territories = { transport.unit.position for transport in possible_transports }

    starting_territory = game_map.name_map[source]
    coastal_adjacencies = reduce(set.__or__, [game_map.adjacency[coast.name] for coast in starting_territory.coasts])
    coastal_adjacencies = list(filter(lambda t: isinstance(game_map.name_map[t], SeaTerritory), coastal_adjacencies))
    to_visit = [
        possible_transport_territory
        for possible_transport_territory in possible_transport_territories
        if any(possible_transport_territory in coastal_adjacency for coastal_adjacency in coastal_adjacencies)
    ]

    while len(to_visit) > 0:
        visiting = to_visit.pop()
        visited.add(visiting)
        # if the convoy was disrupted, we can't use it as part of our chain
        if not _resolve(game_map, command_map, command_map.get_home_command(visiting)):
            continue

        adjacent = [game_map.name_map[adj] for adj in game_map.adjacency[visiting]]

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


#----------------------
# move
#----------------------
def _adjudicate_move(game_map, command_map, command):
    assert isinstance(command, MoveCommand) or isinstance(command, ConvoyMoveCommand)

    attack_strength = _attack_strength(game_map, command_map, command)

    prevent_combatants     = _get_prevent_combatants(command_map, command)
    high_prevent_strength = max([_prevent_strength(game_map, command_map, prevent_combatant)
                                 for prevent_combatant in prevent_combatants] + [0])
    if attack_strength <= high_prevent_strength:
        return False

    head_to_head_combatant = _get_head_to_head_combatant(game_map, command_map, command)
    if head_to_head_combatant is not None:
        return attack_strength > _defend_strength(game_map, command_map, head_to_head_combatant)
    return attack_strength > _hold_strength(game_map, command_map, command.destination)


def _get_prevent_combatants(command_map, command):
    direct_combatants = command_map.get_attackers(command.destination)
    convoy_combatants = command_map.get_convoy_attackers(command.destination)
    combatants = direct_combatants + convoy_combatants
    combatants = filter(lambda c: c != command, combatants)
    return combatants


def _get_head_to_head_combatant(game_map, command_map, command):
    if isinstance(command, ConvoyMoveCommand):
        return None
    potential_attacker = command_map.get_home_command(command.destination)
    if potential_attacker is not None:
        if isinstance(potential_attacker, MoveCommand):
            attacked_territory = game_map.name_map[potential_attacker.destination]
            position_territory = game_map.name_map[command.unit.position]
            if position_territory.same_territory(attacked_territory):
                return potential_attacker
    return None


def _attack_strength(game_map, command_map, command):
    if isinstance(command, ConvoyMoveCommand):
        if not _has_path(game_map, command_map, command):
            return 0
    attacked_command = command_map.get_home_command(command.destination)
    supporters = command_map.get_supports(command.unit.position, command.destination)
    supporters = filter(lambda c: _resolve(game_map, command_map, c), supporters)

    if attacked_command is None:
        return 1 + len(list(supporters))
    if _get_head_to_head_combatant(game_map, command_map, command) is None:
        if isinstance(attacked_command, MoveCommand) or isinstance(attacked_command, ConvoyMoveCommand):
            if _resolve(game_map, command_map, attacked_command):
                return 1 + len(list(supporters))
    if attacked_command.player.name == command.player.name:
        return 0

    supporters = filter(lambda c: c.player.name != attacked_command.player.name, supporters)
    return 1 + len(list(supporters))


def _prevent_strength(game_map, command_map, command):
    if isinstance(command, ConvoyMoveCommand):
        if not _has_path(game_map, command_map, command):
            return 0
    head_to_head_combatant = _get_head_to_head_combatant(game_map, command_map, command)
    if head_to_head_combatant is not None:
        if _resolve(game_map, command_map, head_to_head_combatant):
            return 0

    supporters = command_map.get_supports(command.unit.position, command.destination)
    supporters = filter(lambda c: _resolve(game_map, command_map, c), supporters)
    return 1 + len(list(supporters))


def _defend_strength(game_map, command_map, command):
    supporters = command_map.get_supports(command.unit.position, command.destination)
    supporters = filter(lambda c: _resolve(game_map, command_map, c), supporters)
    return 1 + len(list(supporters))


def _hold_strength(game_map, command_map, territory):
    home_command = command_map.get_home_command(territory)
    if home_command is None:
        return 0
    if isinstance(home_command, MoveCommand) or isinstance(home_command, ConvoyMoveCommand):
        return 0 if _resolve(game_map, command_map, home_command) else 1
    supporters = command_map.get_supports(territory, territory)
    supporters = filter(lambda c: _resolve(game_map, command_map, c), supporters)
    return 1 + len(list(supporters))


#----------------------
# support
#----------------------
def _adjudicate_support(game_map, command_map, command):
    assert isinstance(command, SupportCommand)
    if _invalid_support(command_map, command):
        return False
    if len(_indirect_non_convoy_attackers(command_map, command)) > 0:
        return False
    for convoy_attacker in _indirect_convoy_attackers(command_map, command):
        if _has_path(game_map, command_map, convoy_attacker):
            return False
    return not _is_dislodged(game_map, command_map, command.unit)


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


def _is_dislodged(game_map, command_map, unit):
    """
    Determines if the unit will be dislodged by a different move, assuming it stays in place.
    Please note that this function does not indicate whether the unit _will_ stay in place.
    """
    return any((_resolve(game_map, command_map, attack) for attack in _attackers(game_map, command_map, unit)))


def _attackers(game_map, command_map, unit):
    filtered = command_map.get_attackers(unit.position)
    filtered = filter(
        lambda c: isinstance(c, MoveCommand) or isinstance(c, ConvoyMoveCommand),
        filtered,
    )
    filtered = filter(
        lambda c: game_map.name_map[c.destination].same_territory(game_map.name_map[unit.position]),
        filtered,
    )

    return list(filtered)


#----------------------
# Retreats
#----------------------
def compute_retreats(game_map, command_map, commands, resolutions):
    player_results = defaultdict(dict)
    occupied_territories = _get_occupations(game_map, commands, resolutions)

    for command in commands:
        current_position = command.unit.position
        if resolutions[current_position]:
            if isinstance(command, MoveCommand) or isinstance(command, ConvoyMoveCommand):
                moved_unit = Unit(command.unit.unit_type, command.destination)
                player_results[command.player.name][moved_unit] = None
            else:
                player_results[command.player.name][command.unit] = None
        else:
            direct_attackers = list(filter(
                lambda c: resolutions[c.unit.position],
                command_map.get_attackers(current_position),
            ))
            convoy_attackers = list(filter(
                lambda c: resolutions[c.unit.position],
                command_map.get_convoy_attackers(current_position),
            ))
            attackers = direct_attackers + convoy_attackers
            if len(attackers) == 0:
                player_results[command.player.name][command.unit] = None
            else:
                retreat_options = game_map.adjacency[current_position]
                retreat_options = filter(
                    lambda t: t not in occupied_territories,
                    retreat_options,
                )
                retreat_options = filter(
                    lambda t: all(t not in _applicable_territories(game_map, attacker.unit.position)
                                  for attacker in direct_attackers),
                    retreat_options,
                )
                retreat_options = filter(
                    lambda t: _hold_strength(game_map, command_map, t) == 0,
                    retreat_options,
                )
                retreat_options = filter(
                    lambda t: all(_prevent_strength(game_map, command_map, attacker) == 0
                                  for attacker in command_map.get_attackers(t)),
                    retreat_options,
                )

                player_results[command.player.name][command.unit] = set(retreat_options)

    return player_results


def _applicable_territories(game_map, territory_name):
    territory = game_map.name_map[territory_name]
    applicable = { territory_name }
    if isinstance(territory, LandTerritory):
        applicable |= { coast.name for coast in territory.coasts }
    elif isinstance(territory, CoastTerritory):
        applicable.add(territory.parent.name)
        applicable |= { coast.name for coast in territory.parent.coasts }

    return applicable


def _get_occupations(game_map, commands, resolutions):
    occupations = set()
    for command in commands:
        if isinstance(command, MoveCommand) or isinstance(command, ConvoyMoveCommand):
            if resolutions[command.unit.position]:
                occupations |= _applicable_territories(game_map, command.destination)
            else:
                occupations |= _applicable_territories(game_map, command.unit.position)
        else:
            occupations |= _applicable_territories(game_map, command.unit.position)

    return occupations


def _attacked_by_other_unit(command_map, command, territory):
    attackers = command_map.get_attackers(territory) + command_map.get_convoy_attackers(territory)
    attackers = filter(lambda c: c != command, attackers)
    return len(list(attackers)) > 0
