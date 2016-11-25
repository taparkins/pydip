from map.predefined import vanilla_dip
from player.command.command import MoveCommand, SupportCommand, ConvoyMoveCommand, ConvoyTransportCommand, HoldCommand
from player.player import Player
from test.command_helper import CommandType
from turn.resolve import resolve_turn


class TurnHelper():
    def __init__(self, player_helpers, map=vanilla_dip.generate_map()):
        self.map = map
        self.players = {
            player_helper.name : Player(player_helper.name, map, player_helper.get_starting_configuration())
            for player_helper in player_helpers
        }
        self.commands = self._build_commands(player_helpers)

    def resolve(self):
        return resolve_turn(self.map, self.commands)

    def _build_commands(self, player_helpers):
        commands = []
        for player_helper in player_helpers:
            player = self.players[player_helper.name]
            for command_helper in player_helper.command_helpers:
                commands.append(self._build_command(player, command_helper))
        return commands

    def _build_command(self, player, command):
        unit = self._find_unit(command.unit)
        if command.type == CommandType.MOVE:
            return MoveCommand(player, unit, command.destination)
        if command.type == CommandType.SUPPORT:
            supported_unit = self._find_unit(command.source)
            return SupportCommand(player, unit, supported_unit, command.destination)
        if command.type == CommandType.CONVOY_MOVE:
            return ConvoyMoveCommand(player, unit, command.destination)
        if command.type == CommandType.CONVOY_TRANSPORT:
            transported_unit = self._find_unit(command.source)
            return ConvoyTransportCommand(player, unit, transported_unit, command.destination)
        if command.type == CommandType.HOLD:
            return HoldCommand(player, unit)
        raise ValueError("Invalid command type: {}".format(command.type))

    def _find_unit(self, territory):
        for player in self.players.values():
            for unit in player.units:
                if unit.position == territory:
                    return unit
        raise ValueError("Unable to find unit with position {}".format(territory))