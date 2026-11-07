from abc import ABC, abstractmethod
from typing import Optional
import pygame

from tilecraft.constants import ITEM_IMAGE_MAPPING, Context, Item


class Widget(ABC):
    """
        Widget is a collection of images, rects, and text bundled together to be rendered on a Screen
    """

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
            Handle an event, returning true iff an event was handled
        """
        return False

    def update(self, fps: float) -> None:
        """
            Update the widget
        """
        return None


    @abstractmethod
    def render(self, surface: pygame.Surface, context: Context) -> None:
        """
            Render the widget
        """

class ItemContainerWidget(Widget):
    """
        Base class for all inventory-related container widgets
    """

    @staticmethod
    def _surface_from(context: Context, item: Optional[Item]) -> pygame.Surface:
        """
            Returns the renderable surface for a slot
        """
        if item is None:
            return context.INFOBAR_IMAGES["slot"]
        return context.ITEM_IMAGES[ITEM_IMAGE_MAPPING[item.name]]

    @staticmethod
    def _quantity_from(item: Optional[Item]) -> str:
        """
            Returns the renderable number for a slot
        """
        if item is None or item.number == 1:
            return ""
        return str(item.number)
