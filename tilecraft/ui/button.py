import pygame


class Button:
    """
        Button UI element 
    """

    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font, *, enabled: bool = True) -> None:
        self.rect = rect
        self.text = text
        self.font = font
        self.enabled = enabled

        self.hovered = False
        self.pressed = False

        self.background_colour = pygame.Color("#303D4B")
        self.hover_colour = pygame.Color("#415162")
        self.pressed_colour = pygame.Color("#526170")
        self.disabled_colour = pygame.Color("#252B33")
        self.border_colour = pygame.Color("#FFFFFF")
        self.text_colour = pygame.Color("#FFFFFF")
        self.disabled_text_colour = pygame.Color("#77818C")

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle one Pygame event.

        Returns True only when the button is successfully clicked.
        """

        if not self.enabled:
            self.pressed = False
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            clicked = self.pressed and self.rect.collidepoint(event.pos)
            self.pressed = False
            return clicked

        return False

    def update(self) -> None:
        """Update the hover state."""

        self.hovered = self.enabled and self.rect.collidepoint(pygame.mouse.get_pos())

        # Stop the pressed appearance if the mouse is no longer held.
        if self.pressed and not pygame.mouse.get_pressed()[0]:
            self.pressed = False

    def render(self, surface: pygame.Surface) -> None:
        """Draw the button."""

        if not self.enabled:
            background = self.disabled_colour
            text_colour = self.disabled_text_colour
        elif self.pressed:
            background = self.pressed_colour
            text_colour = self.text_colour
        elif self.hovered:
            background = self.hover_colour
            text_colour = self.text_colour
        else:
            background = self.background_colour
            text_colour = self.text_colour

        pygame.draw.rect(surface, background, self.rect, border_radius=8)

        pygame.draw.rect(surface, self.border_colour, self.rect, width=2, border_radius=8)

        text_surface = self.font.render(self.text, True, text_colour)
        text_rect = text_surface.get_rect(center=self.rect.center)

        surface.blit(text_surface, text_rect)