from player.command.command import ConvoyTransportCommand, MoveCommand

"""
Check if a provided convoy transport command is disrupted by any other movement commands

convoy_command: ConvoyTransportCommand to check for disruption
commands: Command[] representing all commands for the turn

Returns true if any MoveCommand moves into the territory occupied by the transport. False
otherwise.
"""
def convoy_is_disrupted(convoy_command, commands):
    assert isinstance(convoy_command, ConvoyTransportCommand)

    return any([
        disruptor for disruptor in commands
        if (isinstance(disruptor, MoveCommand) and
            disruptor.destination == convoy_command.unit.position)
    ])