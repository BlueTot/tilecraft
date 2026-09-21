import math
import pygame

from tilecraft import ASSETS_DIR
from tilecraft.constants import Coordinate, Context
from tilecraft.ui.widget import Widget
from tilecraft.inventory import Experience
from tilecraft.player_info import Health, Hunger


class ExperienceBarWidget(Widget):
    """
        Experience bar rendered on the main game screen
    """

    def __init__(self, experience: Experience):
        self.experience = experience 
        self.__font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 45)


    def handle_event(self, event: pygame.event.Event) -> None:
        pass


    def render(self, surface: pygame.Surface, context: Context) -> None:
        levels = self.experience.levels

        try:
            percent_xp_to_next_level = (levels - math.floor(levels))
        except ZeroDivisionError:
            percent_xp_to_next_level = 0

        pygame.draw.rect(surface, "#72a34c", (5, 630, round(percent_xp_to_next_level * 738), 30))
        pygame.draw.rect(surface, "#424d42", (round(percent_xp_to_next_level * 738) + 5, 630, round((1 - percent_xp_to_next_level) * 738), 30))

        for i in range(18):
            pygame.draw.rect(surface, (0, 0, 0), (i * 41 + 5, 630, 41, 30), 2)

        experience_number = self.__font.render(str(math.floor(levels)), True, '#82b054', (255, 255, 255))
        experience_number_r = experience_number.get_rect()
        experience_number_r.center = (378, 615)
        surface.blit(experience_number, experience_number_r)  # Experience Number


class HealthBarWidget(Widget):
    """
        Health bar widget to be rendered on the main game screen
    """


    def __init__(self, health: Health):
        self.health = health
        self.__coordinates: list[Coordinate] = []
        for i in range(10):
            self.__coordinates.append(Coordinate(7 + 35*i, 592))


    def handle_event(self, event) -> bool:
        return False


    def render(self, surface: pygame.Surface, context: Context) -> None:
        curr = self.health.value 
        for coordinate in self.__coordinates:
            if curr >= 2:
                image = context.INFOBAR_IMAGES["full_heart"]
                curr -= 2
            elif curr == 1:
                image = context.INFOBAR_IMAGES["half_heart"] 
                curr -= 1
            else:
                image = context.INFOBAR_IMAGES["empty_heart"] 
            surface.blit(image, (coordinate.x, coordinate.y))


class HungerBarWidget(Widget):
    """
        Hunger bar widget to be rendered on the main game screen
    """


    def __init__(self, hunger: Hunger):
        self.hunger = hunger
        self.__coordinates:list[Coordinate] = []
        for i in range(10):
            self.__coordinates.append(Coordinate(715 - 34*i, 592))


    def handle_event(self, event):
        pass


    def render(self, surface: pygame.Surface, context: Context):
        curr = self.hunger.value 
        for coordinate in self.__coordinates:
            if curr >= 2:
                image = context.INFOBAR_IMAGES["full_hunger"]
                curr -= 2
            elif curr == 1:
                image = context.INFOBAR_IMAGES["half_hunger"] 
                curr -= 1
            else:
                image = context.INFOBAR_IMAGES["empty_hunger"] 
            surface.blit(image, (coordinate.x, coordinate.y))
