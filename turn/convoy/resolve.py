from player.command.command import ConvoyTransportCommand, HoldCommand, ConvoyMoveCommand
from turn.convoy.disruption import convoy_is_disrupted
from turn.convoy.check_chains import convoy_chain_exists

"""
Given full list of commands for a turn, reduce any unsuccessful convoy actions
to holds. This does not include handling support checks, which must be done
after support cuts has been checked.

map: Map representing full game board
commands: Command[] representing all commands issued for the turn

returns a modified version of commands where all invalidated convoy actions have
been reduced to holds.
"""
def simplify_convoy_commands(map, commands):
    reduced_commands = _disrupt_convoys(commands)
    reduced_commands = _reduce_transports(reduced_commands)
    reduced_commands = _reduce_moves(map, reduced_commands)

    # We want to get all ineffective convoys reduced to holds, so repeat until fixed
    if reduced_commands != commands:
        reduced_commands = simplify_convoy_commands(map, reduced_commands)
    return reduced_commands

def _disrupt_convoys(commands):
    updated_commands = []
    for command in commands:
        if isinstance(command, ConvoyTransportCommand):
            if convoy_is_disrupted(command, commands):
                updated_commands.append(HoldCommand(command.player, command.unit))
                continue
        updated_commands.append(command)
    return updated_commands

def _reduce_transports(commands):
    updated_commands = []
    for command in commands:
        if isinstance(command, ConvoyTransportCommand):
            transported_unit_command = None
            for subcommand in commands:
                if subcommand.unit == command.transported_unit:
                    transported_unit_command = subcommand
                    break

            if (not isinstance(transported_unit_command, ConvoyMoveCommand) or
                transported_unit_command.destination != command.destination):
                updated_commands.append(HoldCommand(command.player, command.unit))
                continue

        updated_commands.append(command)
    return updated_commands

def _reduce_moves(map, commands):
    updated_commands = []
    for command in commands:
        if isinstance(command, ConvoyMoveCommand):
            if not convoy_chain_exists(map, command, commands):
                updated_commands.append(HoldCommand(command.player, command.unit))
                continue
        updated_commands.append(command)
    return updated_commands