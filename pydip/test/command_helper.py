from enum import Enum


class CommandType(Enum):
    MOVE = 0
    SUPPORT = 1
    CONVOY_MOVE = 2
    CONVOY_TRANSPORT = 3
    HOLD = 5


class CommandHelper:
    """ CommandType, indicating type for command """
    command_type = None

    def __init__(self, command_type, unit_type, unit, *args):
        self.command_type = command_type
        self.unit_type = unit_type
        self.unit = unit
        self._init_args(command_type, args)

    def _init_args(self, command_type, args):
        if command_type == CommandType.MOVE:
            self._init_move(args)
        elif command_type == CommandType.SUPPORT:
            self._init_support(args)
        elif command_type == CommandType.CONVOY_MOVE:
            self._init_convoy_move(args)
        elif command_type == CommandType.CONVOY_TRANSPORT:
            self._init_convoy_transport(args)
        elif command_type == CommandType.HOLD:
            self._init_hold(args)
        else:
            raise ValueError("Invalid type: {}".format(command_type))

    def _init_move(self, args):
        assert len(args) == 1
        self.destination = args[0]

    def _init_support(self, args):
        assert len(args) == 2
        self.source = args[0]
        self.destination = args[1]

    def _init_convoy_move(self, args):
        assert len(args) == 1
        self.destination = args[0]

    def _init_convoy_transport(self, args):
        assert len(args) == 2
        self.source = args[0]
        self.destination = args[1]

    @staticmethod
    def _init_hold(args):
        assert len(args) == 0


class RetreatCommandType(Enum):
    MOVE = 0
    DISBAND = 1


class RetreatCommandHelper:
    """ RetreatCommandType, indicating type for command """
    command_type = None

    def __init__(self, command_type, retreat_map, unit_type, unit, *args):
        self.command_type = command_type
        self.retreat_map = retreat_map
        self.unit_type = unit_type
        self.unit = unit
        self._init_args(command_type, args)

    def _init_args(self, command_type, args):
        if command_type == RetreatCommandType.MOVE:
            self._init_move(args)
        elif command_type == RetreatCommandType.DISBAND:
            self._init_disband(args)
        else:
            raise ValueError("Invalid type: {}".format(command_type))

    def _init_move(self, args):
        assert len(args) == 1
        self.destination = args[0]

    @staticmethod
    def _init_disband(args):
        assert len(args) == 0


class AdjustmentCommandType(Enum):
    CREATE = 0
    DISBAND = 1


class AdjustmentCommandHelper:
    """ AdjustmentCommandType, indicating type for command """
    type = None

    def __init__(self, command_type, unit_type, territory):
        self.type = command_type
        self.unit_type = unit_type
        self.territory = territory
