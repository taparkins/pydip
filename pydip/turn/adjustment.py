from copy import deepcopy

from pydip.map.map import OwnershipMap
from pydip.player.command.adjustment_command import AdjustmentCommand, AdjustmentCreateCommand, AdjustmentDisbandCommand


def calculate_adjustments(ownership_map, player_units):
    """
    Given a map of current ownership, and a map of new unit positions (after
    retreats have been resolved), this function will compute a new ownership
    map as well as what adjustments each player must perform. NOTE: this
    function has no knowledge of Spring vs Fall turns, so the caller should
    only use this after retreats in the Fall.

    ownership_map should be an OwnershipMap for the current game.

    player_units should be the output from turn.retreat.resolve_retreats --
    that is, a map of player names to sets of units after retreat resolution.

    This function returns two values: First, a new OwnershipMap updated for
    new unit positions. Second, a map of player names to integers which
    represent their adjustment requirements. Positive integers denote players
    who are allowed to build units this turn. Negative integers indicate the
    player must disband units this turn.
    """
    all_players = ownership_map.owned_territories.keys()
    new_owned_territories = { player : set() for player in all_players }

    for player in all_players:
        other_player_positions = set()
        for other_player in all_players:
            if other_player != player:
                other_player_positions |= {
                    ownership_map.supply_map.game_map.relevant_name_for_territory(unit.position)
                    for unit in player_units[other_player]
                }

        for territory in ownership_map.owned_territories[player]:
            if territory not in other_player_positions:
                if territory in ownership_map.supply_map.supply_centers:
                    new_owned_territories[player].add(territory)

        for unit in player_units[player]:
            relevant_territory = ownership_map.supply_map.game_map.relevant_name_for_territory(unit.position)
            if relevant_territory in ownership_map.supply_map.supply_centers:
                new_owned_territories[player].add(relevant_territory)

    new_ownership_map = OwnershipMap(
        ownership_map.supply_map,
        new_owned_territories,
        ownership_map.home_territories)

    adjustment_counts = {
        player : len(new_ownership_map.owned_territories[player]) - len(player_units[player])
        for player in all_players
    }

    return new_ownership_map, adjustment_counts


def resolve_adjustment__validated(ownership_map, adjustment_counts, player_units, commands):
    """
    Given an OwnershipMap representing the current board state, a mapping of adjustment expectations
    (expected to be output from calcluate_adjustments), a collection of current player units, and a
    list of AdjustmentCommands to issue, resolves the adjustments and determines what units each
    player will end up with at the end of the turn.

    This specific function also validates several properties that violate strict adherence to Civil
    Disobedience rules. This system typically asserts that users are not allowed to issue illegal
    command sets, and that includes not issuing commands that are required (e.g. Disbanding during
    unit adjustment). However, forcing the caller to follow these atypical policies can potentially
    lead to confusion and invalid game states.

    To that end, there are two adjustment functions provided: one with strict validation, forcing the
    caller to perform sanity checks (and potentially implement Civil Disobedience policies) themselves,
    and a less strictly validated version that applies Civil Disobedience policies automatically when
    improper order counts are provided.


    Both versions return a mapping of player names to sets of Units, representing the units owned by
    each player after adjustments have been resolved.
    """
    _validate_adjustments(ownership_map, adjustment_counts, commands)
    return resolve_adjustment(ownership_map, adjustment_counts, player_units, commands)


def resolve_adjustment(ownership_map, adjustment_counts, player_units, commands):
    new_player_units = deepcopy(player_units)
    for player, count in adjustment_counts.items():
        if count < 0:
            disbands = _find_disbands(player, adjustment_counts, player_units, commands)
            new_player_units[player] -= disbands
        elif count > 0:
            creates = _find_creates(ownership_map.supply_map.game_map, player, adjustment_counts, commands)
            new_player_units[player] |= creates

    return new_player_units


def _find_disbands(player, adjustment_counts, player_units, commands):
    expected_disband_count = -adjustment_counts[player]

    filtered_commands = filter(lambda c: isinstance(c, AdjustmentDisbandCommand), commands)
    filtered_commands = filter(lambda c: c.player.name == player, filtered_commands)
    filtered_commands = list(filtered_commands)

    # if too many disbands, truncate
    if len(filtered_commands) > expected_disband_count:
        filtered_commands = filtered_commands[:expected_disband_count]
    disbands = { command.unit for command in filtered_commands }

    # if too few disbands, begin disbanding units in alphabetical order
    while len(disbands) < expected_disband_count:
        remaining_units = sorted(
            list(set(player_units[player]) - disbands),
            key = lambda u: u.position.lower()
        )
        disbands.add(remaining_units[0])

    return disbands


def _find_creates(game_map, player, adjustment_counts, commands):
    permitted_create_count = adjustment_counts[player]

    filtered_commands = filter(lambda c: isinstance(c, AdjustmentCreateCommand), commands)
    filtered_commands = filter(lambda c: c.player.name == player, filtered_commands)
    filtered_commands = list(filtered_commands)

    # if two creates on same territory, keep first only
    territories_with_creation = set()
    preserved_commands = []
    for command in filtered_commands:
        relevant_name = game_map.relevant_name_for_territory(command.unit.position)
        if relevant_name in territories_with_creation:
            continue
        territories_with_creation.add(relevant_name)
        preserved_commands.append(command)

    # if too many creates, truncate
    if len(preserved_commands) > permitted_create_count:
        preserved_commands = preserved_commands[:permitted_create_count]
    return { command.unit for command in preserved_commands }


def _validate_adjustments(ownership_map, adjustment_counts, commands):
    assert all(isinstance(command, AdjustmentCommand) for command in commands)

    provided_adjustment_terriories = dict()
    for command in commands:
        player = command.player.name
        game_map = ownership_map.supply_map.game_map
        if isinstance(command, AdjustmentCreateCommand):
            if player not in provided_adjustment_terriories:
                provided_adjustment_terriories[player] = set()
            elif adjustment_counts[player] < 0:
                raise AssertionError("{} attempting to Create when required to Disband".format(player))
            elif len(provided_adjustment_terriories[player]) >= adjustment_counts[player]:
                raise AssertionError("{} attempting to Create too many units in one turn".format(player))

            relevant_command_territory = game_map.relevant_name_for_territory(command.unit.position)
            if relevant_command_territory in provided_adjustment_terriories[player]:
                raise AssertionError("{} attempting to Create multiple units in same territory".format(player))

            provided_adjustment_terriories[player].add(relevant_command_territory)
        elif isinstance(command, AdjustmentDisbandCommand):
            if player not in provided_adjustment_terriories:
                provided_adjustment_terriories[player] = set()
            elif adjustment_counts[player] > 0:
                raise AssertionError("{} attempting to Disband when expected to Create".format(player))
            elif len(provided_adjustment_terriories[player]) >= -adjustment_counts[player]:
                raise AssertionError("{} attempting to Disband too many units in one turn".format(player))

            relevant_command_territory = game_map.relevant_name_for_territory(command.unit.position)
            if relevant_command_territory in provided_adjustment_terriories[player]:
                raise AssertionError("{} attempting to Disband same unit multiple times".format(player))

            provided_adjustment_terriories[player].add(relevant_command_territory)
        else:
            raise AssertionError("Unexpected AdjustmentCommand type")

    for player, count in adjustment_counts.items():
        if count < 0:
            if len(provided_adjustment_terriories.get(player, set())) != -count:
                raise AssertionError("{} failed to Disband sufficient units this turn".format(player))
