

class Territory:
    """ String """
    name = None

    def __init__(self, name):
        self.name = name

    def same_territory(self, other):
        return self.name == other.name


class CoastTerritory(Territory):
    """ LandTerritory """
    parent = None

    def __init__(self, name, parent):
        super().__init__(name)
        assert isinstance(parent, LandTerritory)
        self.parent = parent

    def same_territory(self, other):
        relevant_territories = (
            { self.parent.name } |
            { coast.name for coast in self.parent.coasts }
        )
        return other.name in relevant_territories

    def __eq__(self, other):
        if not isinstance(other, CoastTerritory):
            return False

        if self.name != other.name:
            return False

        if self.parent.name != other.parent.name:
            return False

        self_parent_coasts  = { coast.name for coast in self.parent.coasts }
        other_parent_coasts = { coast.name for coast in other.parent.coasts }
        if self_parent_coasts != other_parent_coasts:
            return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)


class LandTerritory(Territory):
    """ CoastTerritory[] """
    coasts = None

    def __init__(self, name, coast_names):
        super().__init__(name)
        self.coasts = []
        for coast_name in coast_names:
            self.coasts.append(CoastTerritory(coast_name, self))

    def same_territory(self, other):
        relevant_territories = (
            { self.name } |
            { coast.name for coast in self.coasts }
        )
        return other.name in relevant_territories

    def __eq__(self, other):
        if not isinstance(other, LandTerritory):
            return False

        if self.name != other.name:
            return False

        self_coasts  = { coast.name for coast in self.coasts }
        other_coasts = { coast.name for coast in other.coasts }
        if self_coasts != other_coasts:
            return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)


class SeaTerritory(Territory):
    def __init__(self, name):
        super().__init__(name)

    def __eq__(self, other):
        if not isinstance(other, SeaTerritory):
            return False
        return self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)
