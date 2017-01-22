
class PlayerHelper:
    def __init__(self, name, command_helpers):
        self.name = name
        self.command_helpers = command_helpers

    def get_starting_configuration(self):
        starting_configs = []
        for command in self.command_helpers:
            starting_configs.append({
                'territory_name' : command.unit,
                'unit_type'      : command.unit_type,
            })
        return starting_configs
