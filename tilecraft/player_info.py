from dataclasses import dataclass

@dataclass
class Health:
    """
        A player's health from 0 to 20
    """
    value: int


@dataclass
class Hunger:
    """
        A player's hunger from 0 to 20
    """
    value: int


class Experience:
    """
        A player's experience is made up of points and levels
        When you get enough points the level increases
    """
    def __init__(self) -> None:
        self.__levels: float = 0

    def add_points(self, experience_points: int) -> None:
        """
            Add a set number of points to the experience counter
        """
        self.__levels += (-1 + (1 + 4 * (experience_points + self.__levels ** 2 + self.__levels)) ** 0.5) / 2 - self.__levels

    @property
    def levels(self) -> float:
        """
            Get number of experience levels
        """
        return self.__levels

    def subtract(self, levels: int) -> None:
        """
            Subtract a set number of levels from the counter
        """
        if self.__levels - levels < 0:
            return
        self.__levels -= levels
