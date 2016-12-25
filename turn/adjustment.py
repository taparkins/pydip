from map.map import OwnershipMap

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
def calculate_adjustments(ownernship_map, player_units):
    all_players = ownernship_map.owned_territories.keys()
    new_owned_territories = { player : set() for player in all_players }

    for player in all_players:
        other_player_positions = set()
        for other_player in all_players:
            if other_player != player:
                other_player_positions |= { unit.position for unit in player_units[other_player] }

        for territory in ownernship_map.owned_territories[player]:
            if territory not in other_player_positions:
                if territory in ownernship_map.supply_map.supply_centers:
                    new_owned_territories[player].add(territory)

        for unit in player_units[player]:
            if unit.position in ownernship_map.supply_map.supply_centers:
                new_owned_territories[player].add(unit.position)

    new_ownership_map = OwnershipMap(
        ownernship_map.supply_map,
        ownernship_map.owned_territories,
        ownernship_map.home_territories)

    adjustment_counts = {
        player : len(new_ownership_map.owned_territories[player]) - len(player_units[player])
        for player in all_players
    }

    return new_ownership_map, adjustment_counts