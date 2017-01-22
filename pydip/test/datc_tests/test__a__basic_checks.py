import pytest

from pydip.map.predefined.vanilla_dip import generate_map
from pydip.player.command.command import (
    ConvoyMoveCommand,
    ConvoyTransportCommand,
    HoldCommand,
    MoveCommand,
    SupportCommand,
)
from pydip.player.player import Player
from pydip.player.unit import UnitTypes, Unit
from pydip.turn.resolve import resolve_turn


def test_a_1__check_move_to_non_neighboring_territory_fails():
    """ ENGLAND: F North Sea -> Picardy """
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'North Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("England", game_map, starting_configuration)

    with pytest.raises(AssertionError):
        MoveCommand(player, player.units[0], 'Picardy Coast')


def test_a_2__check_army_to_sea_territory_fails():
    """ ENGLAND: A Liverpool -> Irish Sea """
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Liverpool', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("England", game_map, starting_configuration)

    with pytest.raises(AssertionError):
        MoveCommand(player, player.units[0], 'Irish Sea')


def test_a_3__check_fleet_to_land_territory_fails():
    """ GERMANY: F Kiel Coast -> Munich """
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Kiel Coast', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Germany", game_map, starting_configuration)

    with pytest.raises(AssertionError):
        MoveCommand(player, player.units[0], 'Munich')


def test_a_4__check_move_to_same_territory():
    """ GERMANY: F Kiel Coast -> Kiel Coast """
    # We treat this as identical to a Hold command
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Kiel Coast', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Germany", game_map, starting_configuration)

    move = MoveCommand(player, player.units[0], 'Kiel Coast')
    assert move == HoldCommand(player, player.units[0])


def test_a_5__check_convoy_to_same_territory_fails():
    """
    ENGLAND: A Convoy Yorkshire -> Yorkshire
             F North Sea Transport Yorkshire -> Yorkshire
    """
    # Modified from original check: we treat both commands as illegal, so no resolution check needed.
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Yorkshire', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'North Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("England", game_map, starting_configuration)

    with pytest.raises(AssertionError):
        ConvoyMoveCommand(player, player.units[0], 'Yorkshire')
    with pytest.raises(AssertionError):
        ConvoyTransportCommand(player, player.units[1], player.units[0], 'Yorkshire')


def test_a_6__check_player_cannot_command_other_players_units():
    """
    (all troops belong to England)
    GERMANY: F London Coast -> North Sea
             A Liverpool Hold
             A Wales Support Liverpool Hold
             A Convoy Wales -> Picardy
             F English Channel Transport Wales -> Picardy
    """
    # Extended from original check: various command types added, since all should fail
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'London Coast', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Liverpool', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'Wales', 'unit_type': UnitTypes.TROOP},
        {'territory_name': 'English Channel', 'unit_type': UnitTypes.FLEET},
    ]
    england = Player("England", game_map, starting_configuration)
    germany = Player("Germany", game_map, [])

    with pytest.raises(AssertionError):
        MoveCommand(germany, england.units[0], 'North Sea')
    with pytest.raises(AssertionError):
        HoldCommand(germany, england.units[1])
    with pytest.raises(AssertionError):
        SupportCommand(germany, england.units[2], england.units[1], 'Liverpool')
    with pytest.raises(AssertionError):
        ConvoyMoveCommand(germany, england.units[2], 'Picardy')
    with pytest.raises(AssertionError):
        ConvoyTransportCommand(germany, england.units[3], england.units[2], 'Picardy')


def test_a_7__fleet_cannot_be_convoyed():
    """
    ENGLAND: F Convoy London Coast -> Belgium Coast
             F North Sea Transport London Coast -> Belgium Coast
    """
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'London Coast', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'North Sea', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("England", game_map, starting_configuration)

    with pytest.raises(AssertionError):
        ConvoyMoveCommand(player, player.units[0], 'Belgium Coast')
    with pytest.raises(AssertionError):
        ConvoyTransportCommand(player, player.units[1], player.units[0], 'Belgium Coast')


def test_a_8__check_unit_cannot_support_itself():
    """ FRANCE: F Trieste Coast Support Trieste Coast Hold """
    # Modified from original check: this command is considered illegal, so no resolution check is made
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Trieste Coast', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("France", game_map, starting_configuration)

    with pytest.raises(AssertionError):
        SupportCommand(player, player.units[0], player.units[0], 'Trieste')


def test_a_9__fleets_must_follow_coastlines():
    """ ITALY: F Rome Coast -> Venice Coast """
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Rome Coast', 'unit_type': UnitTypes.FLEET},
    ]
    player = Player("Italy", game_map, starting_configuration)

    with pytest.raises(AssertionError):
        MoveCommand(player, player.units[0], 'Venice Coast')


def test_a_10__support_of_unreachable_destination_fails():
    """ ITALY: F Rome Coast Support Apulia -> Venice """
    game_map = generate_map()
    starting_configuration = [
        {'territory_name': 'Rome Coast', 'unit_type': UnitTypes.FLEET},
        {'territory_name': 'Apulia', 'unit_type': UnitTypes.TROOP},
    ]
    player = Player("Italy", game_map, starting_configuration)

    with pytest.raises(AssertionError):
        SupportCommand(player, player.units[0], player.units[1], 'Venice')


def test_a_11__simple_bounce():
    """
    AUSTRIA: A Vienna -> Tyrolia
    ITALY:   A Venice -> Tyrolia
    """
    game_map = generate_map()
    austria_starting_configuration = [
        {'territory_name': 'Vienna', 'unit_type': UnitTypes.TROOP},
    ]
    austria = Player("Austria", game_map, austria_starting_configuration)

    italy_starting_configuration = [
        {'territory_name': 'Venice', 'unit_type': UnitTypes.TROOP},
    ]
    italy = Player("Italy", game_map, italy_starting_configuration)

    commands = [
        MoveCommand(austria, austria.units[0], 'Tyrolia'),
        MoveCommand(italy, italy.units[0], 'Tyrolia'),
    ]
    result = resolve_turn(game_map, commands)
    assert result == {
        'Austria' : { Unit(UnitTypes.TROOP, 'Vienna') : None },
        'Italy'   : { Unit(UnitTypes.TROOP, 'Venice') : None },
    }


def test_a_12__three_unit_bounce():
    """
    AUSTRIA: A Vienna -> Tyrolia
    GERMANY: A Munich -> Tyrolia
    ITALY:   A Venice -> Tyrolia
    """
    game_map = generate_map()
    austria_starting_configuration = [
        {'territory_name': 'Vienna', 'unit_type': UnitTypes.TROOP},
    ]
    austria = Player("Austria", game_map, austria_starting_configuration)

    germany_starting_configuration = [
        {'territory_name': 'Munich', 'unit_type': UnitTypes.TROOP},
    ]
    germany = Player("Germany", game_map, germany_starting_configuration)

    italy_starting_configuration = [
        {'territory_name': 'Venice', 'unit_type': UnitTypes.TROOP},
    ]
    italy = Player("Italy", game_map, italy_starting_configuration)

    commands = [
        MoveCommand(austria, austria.units[0], 'Tyrolia'),
        MoveCommand(germany, germany.units[0], 'Tyrolia'),
        MoveCommand(italy, italy.units[0], 'Tyrolia'),
    ]
    result = resolve_turn(game_map, commands)
    assert result == {
        'Austria' : { Unit(UnitTypes.TROOP, 'Vienna') : None },
        'Germany' : { Unit(UnitTypes.TROOP, 'Munich') : None },
        'Italy'   : { Unit(UnitTypes.TROOP, 'Venice') : None },
    }
