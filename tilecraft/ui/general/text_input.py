import pygame

from tilecraft.ui.widget import Widget
from tilecraft.constants import Context


class TextInput(Widget):
    """
        Typing input box UI element
    """

    def __init__(self, rect: pygame.Rect, font: pygame.font.Font, placeholder: str = "", max_length: int = 20) -> None:
        self.rect = rect
        self.font = font
        self.placeholder = placeholder
        self.max_length = max_length

        self.text = ""
        self.active = False
        self.cursor_visible = False
        self.last_cursor_toggle = pygame.time.get_ticks()

    def handle_event(self, event: pygame.event.Event) -> None:

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
            self.cursor_visible = self.active
            self.last_cursor_toggle = pygame.time.get_ticks()

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]

            elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                self.active = False
                self.cursor_visible = False

            elif (event.unicode.isprintable() and len(self.text) < self.max_length):
                proposed_text = self.text + event.unicode

                # Prevent the text from escaping the box.
                available_width = self.rect.width - 24

                if self.font.size(proposed_text)[0] <= available_width:
                    self.text = proposed_text

            self.cursor_visible = True
            self.last_cursor_toggle = pygame.time.get_ticks()

    def update(self, fps: float) -> None:
        if not self.active:
            self.cursor_visible = False
            return

        current_time = pygame.time.get_ticks()

        if current_time - self.last_cursor_toggle >= 500:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle = current_time

    def render(self, surface: pygame.Surface, context: Context) -> None:
        background = "#202732"
        border = "#FFFFFF" if self.active else "#77818C"

        pygame.draw.rect(surface, background, self.rect, border_radius=7)
        pygame.draw.rect(surface, border, self.rect, width=2, border_radius=7)

        padding = 12

        if self.text:
            displayed_text = self.text
            text_colour = "#FFFFFF"
        else:
            displayed_text = self.placeholder
            text_colour = "#77818C"

        text_surface = self.font.render(displayed_text, True, text_colour)
        text_rect = text_surface.get_rect(midleft=(self.rect.left + padding, self.rect.centery))
        surface.blit(text_surface, text_rect)

        if self.active and self.cursor_visible:
            cursor_x = self.rect.left + padding + self.font.size(self.text)[0]
            cursor_top = self.rect.centery - self.font.get_height() // 2
            cursor_bottom = cursor_top + self.font.get_height()

            pygame.draw.line(surface, "#FFFFFF", (cursor_x, cursor_top), (cursor_x, cursor_bottom), width=2)