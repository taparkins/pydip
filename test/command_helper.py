from enum import Enum


class CommandType(Enum):
    MOVE = 0
    SUPPORT = 1
    CONVOY_MOVE = 2
    CONVOY_TRANSPORT = 3
    HOLD = 5

class CommandHelper():
    """ CommandType, indicating type for command """
    type = None

    def __init__(self, type, unit_type, unit, *args):
        self.type = type
        self.unit_type = unit_type
        self.unit = unit
        self._init_args(type, args)

    def _init_args(self, type, args):
        if type == CommandType.MOVE:
            self._init_move(args)
        elif type == CommandType.SUPPORT:
            self._init_support(args)
        elif type == CommandType.CONVOY_MOVE:
            self._init_convoy_move(args)
        elif type == CommandType.CONVOY_TRANSPORT:
            self._init_convoy_transport(args)
        elif type == CommandType.HOLD:
            self._init_hold(args)
        else:
            raise ValueError("Invalid type: {}".format(type))

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

    def _init_hold(self, args):
        assert len(args) == 0