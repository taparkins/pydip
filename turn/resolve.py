from turn.convoy.resolve import simplify_convoy_commands

"""
Returns resulting positions of each unit by considering interactions
of provided list of commands.

Note: assumes that every unit on the map has been issued a command.
If a unit has _not_ been issued a command, you ought to insert a
HoldCommand for that unit by default.

map: Map representing game board
commands: Command[] representing each command issued for this turn

returns a map of Player names to sub-maps representing results of that
player's units. The sub-maps will be maps of Units to an optional set
of territories, representing which territories the unit can retreat to.
If the territory set is not provided, no retreat is required. If the
territory set is provided, a retreat is rezuired. If it is empty, no
retreat is possible.
"""
def resolve_turn(map, commands):
    reduced_commands = simplify_convoy_commands(map, commands)
    # TODO