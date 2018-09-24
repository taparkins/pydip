# This scripts contains an example of how to use PyDip.
from pprint import pprint

from pydip.map.predefined import vanilla_dip
from pydip.player import Player
from pydip.player import command
from pydip.turn import resolve_turn, resolve_retreats, resolve_adjustment

# The test module contains some convenient helpers (not used in this examples,
# in order to better demonstrate how PyDip works)
from pydip.test import CommandType, CommandHelper, PlayerHelper, TurnHelper


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
france = players['France']
units = sorted(france.units)
cmd = command.MoveCommand(france, units[0], 'Mid-Atlantic Ocean')
print('\nCommands\n========\n{}'.format(cmd))
# illegal commands result in an error
try:
    command.MoveCommand(france, units[0], 'Marseilles')
except AssertionError:
    print('Illegal command')


# PyDip can resolve a set of commands
# the pydip test package provides some helpers
commands = []
for name, destinations in dict(
        England=['Norwegian Sea', 'Wales', 'North Sea'],
        France=['Mid-Atlantic Ocean', 'Burgundy', 'Picardy'],
        Germany=['Prussia', 'Holland Coast', 'Burgundy'],
        Italy=['Ionian Sea', 'Naples', 'Tyrolia'],
        Russia=['Livonia', 'Black Sea', 'Livonia Coast', 'Ukraine'],
        Austria=['Serbia', 'Albania Coast', 'Tyrolia'],
        Turkey=['Black Sea', 'Bulgaria', 'Constantinople'],
).items():
    player = players[name]
    # player units are a set, so their order is not guaranteed
    # (so we sort them)
    units = sorted(player.units)
    for i, dest in enumerate(destinations):
        cmd = command.MoveCommand(player, units[i], dest)
        print(cmd)
        commands.append(cmd)

# resolve_turn returns a map of units (at their new positions) that tells
# if and where units must retreat
resolutions = resolve_turn(game_map, commands)
print('\nResolution\n==========')
pprint(resolutions)
