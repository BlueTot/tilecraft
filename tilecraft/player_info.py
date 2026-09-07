import pygame
import math

from tilecraft import ASSETS_DIR
from .constants import Context, Coordinate

class HealthBar:
    def __init__(self):
        self.__COORDINATES: list[Coordinate] = []
        for i in range(10):
            self.__COORDINATES.append(Coordinate(7 + 35*i, 592))

    def render(self, display: pygame.Surface, context: Context, health_value: int):
        curr = health_value
        for coordinate in self.__COORDINATES:
            if curr >= 2:
                image = context.INFOBAR_IMAGES["full_heart"]
                curr -= 2
            elif curr == 1:
                image = context.INFOBAR_IMAGES["half_heart"] 
                curr -= 1
            else:
                image = context.INFOBAR_IMAGES["empty_heart"] 
            display.blit(image, (coordinate.x, coordinate.y))

class HungerBar:
    def __init__(self):
        self.__COORDINATES: list[Coordinate] = []
        for i in range(10):
            self.__COORDINATES.append(Coordinate(715 - 34*i, 592))

    def render(self, display: pygame.Surface, context: Context, hunger_value: int):
        curr = hunger_value
        for coordinate in self.__COORDINATES:
            if curr >= 2:
                image = context.INFOBAR_IMAGES["full_hunger"]
                curr -= 2
            elif curr == 1:
                image = context.INFOBAR_IMAGES["half_hunger"] 
                curr -= 1
            else:
                image = context.INFOBAR_IMAGES["empty_hunger"] 
            display.blit(image, (coordinate.x, coordinate.y))


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
