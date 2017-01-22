from map.map import OwnershipMap
from map.predefined import vanilla_dip
from player.command.adjustment_command import AdjustmentCreateCommand, AdjustmentDisbandCommand
from player.player import Player
from player.unit import Unit
from test.command_helper import AdjustmentCommandType
from turn.adjustment import calculate_adjustments, resolve_adjustment, resolve_adjustment__validated


class AdjustmentHelper():
    def __init__(
            self,
            player_helpers,
            player_units=vanilla_dip.generate_starting_player_units(),
            owned_territories=vanilla_dip.generate_home_territories(),
            home_territories=vanilla_dip.generate_home_territories(),
            supply_map=vanilla_dip.generate_supply_center_map(),
    ):
        self.ownership_map = OwnershipMap(supply_map, owned_territories, home_territories)
        self.players = {
            player_helper.name : Player(
                player_helper.name,
                self.ownership_map.supply_map.map,
                _get_starting_configuration(player_units[player_helper.name]))
            for player_helper in player_helpers
        }
        self.calculate_adjustments(player_units)
        self.commands = self._build_commands(player_helpers)

    def calculate_adjustments(self, player_units):
        self.player_units = player_units
        self.ownership_map, self.adjustment_counts = calculate_adjustments(self.ownership_map, self.player_units)

    def resolve(self):
        return resolve_adjustment(self.ownership_map, self.adjustment_counts, self.player_units, self.commands)

    def resolve__validated(self):
        return resolve_adjustment__validated(self.ownership_map, self.adjustment_counts, self.player_units, self.commands)

    def _build_commands(self, player_helpers):
        commands = []
        for player_helper in player_helpers:
            player = self.players[player_helper.name]
            for command_helper in player_helper.command_helpers:
                commands.append(self._build_command(player, command_helper))
        return commands

    def _build_command(self, player, command):
        unit = Unit(command.unit_type, command.territory)
        if command.type == AdjustmentCommandType.CREATE:
            return AdjustmentCreateCommand(self.ownership_map, player, unit)
        if command.type == AdjustmentCommandType.DISBAND:
            return AdjustmentDisbandCommand(player, unit)
        raise ValueError("Invalid command type: {}".format(command.type))

def _get_starting_configuration(units):
    return [
        { 'territory_name' : unit.position, 'unit_type': unit.unit_type }
        for unit in units
    ]