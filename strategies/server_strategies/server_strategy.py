class ServerStrategy:
    def get_next_move_time(self, game_properties, system, current_time):
        """
        :param game_properties:
        :param counter:
        :param system:
        :param current_time: Time of the game
        :return: Returns the next move time
        """
        raise NotImplementedError("get_next_move_time method has not been implemented within strategy subclass")

    def __str__(self):
        raise NotImplementedError("__str__ method has not been implemented within strategy subclass")