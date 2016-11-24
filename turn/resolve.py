from collections import defaultdict
from enum import Enum

from player.command.command import MoveCommand, ConvoyMoveCommand, ConvoyTransportCommand, SupportCommand
from turn.adjudicate.convoy import adjudicate_convoy_move, adjudicate_convoy_transport
from turn.adjudicate.move import adjudicate_move
from turn.adjudicate.support import adjudicate_support
from turn.command_map import CommandMap
from turn.retreat import compute_retreats

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
def resolve_turn(map, commands):
    command_map = CommandMap(map, commands)
    _init_resolution()
    resolutions = { command.unit.position: _resolve(map, command_map, command) for command in commands }
    return compute_retreats(map, command_map, commands, resolutions)

# Below implementation is taken with minor modification from Lucas Kruijswijk:
# http://www.diplom.org/Zine/S2009M/Kruijswijk/DipMath_Chp6.htm
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

def _resolve(map, command_map, command):
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
    fail_guess_result                 = _adjudicate(map, command_map, command)

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

    resolution_map[command_territory] = True
    state_map[command_territory]      = ResolutionState.GUESSING
    success_guess_result              = _adjudicate(map, command_map, command)

    # If results are consistent, no need for further checking
    if fail_guess_result == success_guess_result:
        for dependent_territory in dependency_sub_set:
            state_map[dependent_territory] = ResolutionState.UNRESOLVED

        resolution_map[command_territory] = fail_guess_result
        state_map[command_territory]      = ResolutionState.RESOLVED
        return fail_guess_result

    # If we got to this point, that means we encountered a paradox that has two
    # consistent outcomes, and we need a backup rule to fully resolve it
    _backup_rule(map, command_map, dependency_sub_set)

    # And because the backup rule may not resolve our own command, we'll need to
    # start fresh just to be sure
    return _resolve(map, command_map, command)

def _adjudicate(map, command_map, command):
    if isinstance(command, MoveCommand):
        return adjudicate_move(map, command_map, command)
    elif isinstance(command, ConvoyMoveCommand):
        return adjudicate_convoy_move(map, command_map, command)
    elif isinstance(command, ConvoyTransportCommand):
        return adjudicate_convoy_transport(map, command_map, command)
    elif isinstance(command, SupportCommand):
        return adjudicate_support(map, command_map, command)
    else:
        raise ValueError("Command unexpected type")

def _backup_rule(map, command_map, dependency_set):
    # TODO: Szykman Rule
    pass
