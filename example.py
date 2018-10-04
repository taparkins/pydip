# This scripts contains an example of how to use PyDip.
from pprint import pprint

from pydip.map.predefined import vanilla_dip
from pydip.player import Player, command
from pydip.turn import resolve_turn, resolve_retreats, resolve_adjustment

# The test module contains some convenient helpers (not used in this examples,
# in order to better demonstrate how PyDip works)
from pydip.test import CommandHelper, PlayerHelper, TurnHelper, CommandType


# PyDip provides a predefined map of vanilla Diplomacy
# the most extensive generator defines the map, supply centers and ownership
vanilla_map = vanilla_dip.generate_starting_ownership_map()
print('Vanilla map\n===========\n\n{}'.format(vanilla_map))
# but in most cases, just the game map is sufficient
game_map = vanilla_map.supply_map.game_map


# vanilla_dip includes a definition that can be used to create players
print('\nPlayers\n=======\n')
players = {}
for name, units in vanilla_dip.generate_starting_player_units().items():
    starting_config = [dict(territory_name=u.position, unit_type=u.unit_type) for u in units]
    players[name] = Player(name, game_map, starting_config)
    print(players[name])


# players can issue commands
england = players['England']
unit = england.find_unit('Liverpool')
cmd = command.MoveCommand(england, unit, 'Wales')
print('\nCommands\n========\n{}'.format(cmd))
# illegal commands result in an error
try:
    command.MoveCommand(england, unit, 'York')
except AssertionError:
    print('Illegal command\n')


# PyDip can resolve a set of commands
# the pydip test package provides some helpers
commands = [cmd]
for name, moves in dict(
        England=[('Edinburgh Coast', 'Norwegian Sea'),
                 ('Liverpool', 'Wales'),
                 ('London Coast', 'North Sea')],
        France=[('Brest Coast', 'Mid-Atlantic Ocean'),
                ('Marseilles', 'Burgundy'),
                ('Paris', 'Picardy')],
        Germany=[('Berlin', 'Prussia'),
                 ('Kiel Coast', 'Holland Coast'),
                 ('Munich', 'Burgundy')],
        Italy=[('Naples Coast', 'Ionian Sea'),
               ('Rome', 'Naples'),
               ('Venice', 'Tyrolia')],
        Russia=[('Moscow', 'Livonia'),
                ('Sevastopol Coast', 'Black Sea'),
                ('St. Petersburg South Coast', 'Livonia Coast'),
                ('Warsaw', 'Ukraine')],
        Austria=[('Budapest', 'Serbia'),
                 ('Trieste Coast', 'Albania Coast'),
                 ('Vienna', 'Tyrolia')],
        Turkey=[('Ankara Coast', 'Black Sea'),
                ('Constantinople', 'Bulgaria'),
                ('Smyrna', 'Constantinople')],
).items():
    player = players[name]
    for position, dest in moves:
        unit = player.find_unit(position)
        cmd = command.MoveCommand(player, unit, dest)
        print(cmd)
        commands.append(cmd)

# resolve_turn returns a map of units (at their new positions) that tells
# if and where units must retreat
resolutions = resolve_turn(game_map, commands)
print('\nResolution\n==========')
pprint(resolutions)
