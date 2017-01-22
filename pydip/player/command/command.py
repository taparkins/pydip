from pydip.map.territory import SeaTerritory
from pydip.player.helpers import (
    unit_can_enter,
    unit_can_support,
    territory_is_convoy_compatible,
)
from pydip.player.unit import UnitTypes


class Command:
    """ Player -- who is issuing command """
    player = None

    """ Unit -- unit being issued command """
    unit = None

    def __init__(self, player, unit):
        assert unit in player.units
        self.player = player
        self.unit = unit

    def __eq__(self, other):
        return ((isinstance(other, Command)) and
                (self.player.name == other.player.name) and
                (self.unit == other.unit))

    def __ne__(self, other):
        return not self.__eq__(other)


class MoveCommand(Command):
    """
    String -- Name of territory being moved to.
      * Must be adjacent or equal to unit's current territory
      * Must be legal for unit to enter this territory
    """
    destination = None

    def __init__(self, player, unit, destination):
        super().__init__(player, unit)
        game_map = self.player.game_map
        assert destination in game_map.name_map
        assert (
            unit_can_enter(game_map, unit, game_map.name_map[destination]) or
            unit.position == destination
        )
        self.destination = destination

    def __eq__(self, other):
        return (super(MoveCommand, self).__eq__(other) and
                isinstance(other, MoveCommand) and
                self.destination == other.destination)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '{}: {} {} -> {}'.format(
            self.player.name,
            self.unit.unit_type,
            self.unit.position,
            self.destination,
        )


class HoldCommand(MoveCommand):
    """ Holding is really just moving to your current position """
    def __init__(self, player, unit):
        super().__init__(player, unit, unit.position)

    def __repr__(self):
        return '{}: {} {} Hold'.format(
            self.player.name,
            self.unit.unit_type,
            self.unit.position,
        )


class SupportCommand(Command):
    """ Unit -- unit to support """
    supported_unit = None

    """
    String -- name of territory to support into.
      * Must be adjacent to unit's current territory
      * Must be legal for unit to enter this territory
      * Must be adjacent or identical to supported_unit's current territory
      * Must be legal for supported_unit to support this territory
    """
    destination = None

    def __init__(self, player, unit, supported_unit, destination):
        super().__init__(player, unit)
        self.supported_unit = supported_unit
        self.destination = destination
        game_map = self.player.game_map

        assert destination in game_map.name_map
        destination_territory = game_map.name_map[destination]
        supported_territory   = game_map.name_map[supported_unit.position]

        assert (
            destination == supported_unit.position or
            unit_can_enter(game_map, supported_unit, destination_territory) or
            (supported_unit.unit_type == UnitTypes.TROOP and
             territory_is_convoy_compatible(destination_territory) and
             territory_is_convoy_compatible(supported_territory))
        )
        assert unit_can_support(game_map, unit, destination_territory)

    def __eq__(self, other):
        return (super(SupportCommand, self).__eq__(other) and
                isinstance(other, SupportCommand) and
                self.supported_unit == other.supported_unit and
                self.destination == other.desination)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '{}: {} {} Supports {} {} -> {}'.format(
            self.player.name,
            self.unit.unit_type,
            self.unit.position,
            self.supported_unit.unit_type,
            self.supported_unit.position,
            self.destination,
        )


class ConvoyMoveCommand(Command):
    """
    String -- name of territory convoying to.
      * Must be LandTerritory with at least one coast
    """
    destination = None

    """
    Extra Assertions:
      * unit must be a TROOP
      * unit's current territory must be LandTerritory with at least one coast
      * convoys with destinations equal to the source are illegal
    """

    def __init__(self, player, unit, destination):
        super().__init__(player, unit)
        self.destination = destination
        game_map = self.player.game_map

        current_territory     = game_map.name_map[unit.position]
        destination_territory = game_map.name_map[destination]
        assert current_territory != destination_territory

        assert unit.unit_type == UnitTypes.TROOP
        assert territory_is_convoy_compatible(current_territory)

        assert destination in game_map.name_map
        assert territory_is_convoy_compatible(destination_territory)

    def __eq__(self, other):
        return (super(ConvoyMoveCommand, self).__eq__(other) and
                isinstance(other, ConvoyMoveCommand) and
                self.destination == other.destination)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '{}: {} {} -> {} (Convoy)'.format(
            self.player.name,
            self.unit.unit_type,
            self.unit.position,
            self.destination,
        )


class ConvoyTransportCommand(Command):
    """
    Unit -- unit to convoy.
      * Must be a TROOP
    """
    transported_unit = None

    """
    String -- name of territory convoying to.
      * Must be LandTerritory with at least one coast
    """
    destination = None

    """
    Extra Assertions:
      * unit must be a FLEET
      * unit's current territory must be a SeaTerritory
      * transported unit's current territory must be LandTerritory with at least one coast
      * convoys with destinations equal to the source are illegal
    """

    def __init__(self, player, unit, transported_unit, destination):
        super().__init__(player, unit)
        self.transported_unit = transported_unit
        self.destination = destination
        assert unit.unit_type == UnitTypes.FLEET
        game_map = self.player.game_map

        current_territory = game_map.name_map[unit.position]
        source_territory = game_map.name_map[transported_unit.position]
        destination_territory = game_map.name_map[destination]
        assert source_territory != destination_territory
        assert isinstance(current_territory, SeaTerritory)

        assert transported_unit.unit_type == UnitTypes.TROOP
        assert territory_is_convoy_compatible(source_territory)

        assert destination in game_map.name_map
        assert territory_is_convoy_compatible(destination_territory)

    def __eq__(self, other):
        return (super(ConvoyTransportCommand, self).__eq__(other) and
                isinstance(other, ConvoyTransportCommand) and
                self.transported_unit == other.transported_unit and
                self.destination == other.desination)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '{}: {} {} Transport {} {} -> {} (Convoy)'.format(
            self.player.name,
            self.unit.unit_type,
            self.unit.position,
            self.transported_unit.unit_type,
            self.transported_unit.position,
            self.destination,
        )
