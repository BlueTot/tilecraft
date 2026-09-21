from abc import ABC, abstractmethod
import pygame

from tilecraft.constants import Context


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
