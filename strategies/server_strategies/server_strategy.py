from typing import Dict

class ServerStrategy:
    def get_next_move_time(self, information: Dict) -> float:
        """
        :param information: Dictionary containing game information
        :return:
        """
        raise NotImplementedError("get_next_move_time method has not been implemented within strategy subclass")

    def __str__(self) -> str:
        raise NotImplementedError("__str__ method has not been implemented within strategy subclass")
