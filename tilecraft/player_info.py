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
    def __init__(self) -> None:
        self.__levels: float = 0

    def add_points(self, experience_points: int) -> None:
        self.__levels += (-1 + (1 + 4 * (experience_points + self.__levels ** 2 + self.__levels)) ** 0.5) / 2 - self.__levels

    @property
    def levels(self) -> float:
        return self.__levels

    def subtract(self, levels: int) -> None:
        if self.__levels - levels < 0:
            return
        self.__levels -= levels

class ExperienceBar:
    def __init__(self):
        self.__font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 45)

    def render(self, display: pygame.Surface, levels: float):
        try:
            percent_xp_to_next_level = (levels - math.floor(levels))
        except ZeroDivisionError:
            percent_xp_to_next_level = 0

        # DRAW EXPERIENCE BAR
        pygame.draw.rect(display, "#72a34c", (5, 630, round(percent_xp_to_next_level * 738), 30))
        pygame.draw.rect(display, "#424d42", (round(percent_xp_to_next_level * 738) + 5, 630, round((1 - percent_xp_to_next_level) * 738), 30))
        for i in range(18):
            pygame.draw.rect(display, (0, 0, 0), (i * 41 + 5, 630, 41, 30), 2)
        experience_number = self.__font.render(str(math.floor(levels)), True, '#82b054', (255, 255, 255))
        experience_number_r = experience_number.get_rect()
        experience_number_r.center = (378, 615)
        display.blit(experience_number, experience_number_r)  # Experience Number