from player.command.command import Command


class AdjustmentCommand(Command):
    pass

class AdjustmentDisbandCommand(AdjustmentCommand):
    def __init__(self, player, unit):
        super().__init__(player, unit)
        assert unit in player.units

    def __repr__(self):
        return '{}: {} {} Disband'.format(
            self.player.name,
            self.unit.unit_type,
            self.unit.position,
        )

    def __eq__(self, other):
        return (super(AdjustmentDisbandCommand, self).__eq__(other) and
                isinstance(other, AdjustmentDisbandCommand))

    def __ne__(self, other):
        return not self.__eq__(other)

class AdjustmentCreateCommand(AdjustmentCommand):
    """
    Unlike a traditional command, this one uses the unit to represent the new unit to be created.
    So this command takes an OwnershipMap, representing current board state, to determine if the
    provided unit would be allowed to be created for this player.
    """
    def __init__(self, ownership_map, player, unit):
        super().__init__(player, unit)

        assert ownership_map.territory_is_owned(player.name, unit.position)
        assert ownership_map.territory_is_home(player.name, unit.position)

    def __eq__(self, other):
        return (super(AdjustmentCreateCommand, self).__eq__(other) and
                isinstance(other, AdjustmentCreateCommand))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '{}: {} {} Create'.format(
            self.player.name,
            self.unit.unit_type,
            self.unit.position,
        )