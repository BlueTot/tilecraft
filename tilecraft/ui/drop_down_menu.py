import pygame


class Dropdown:
    """
        Drop down menu UI element
    """

    def __init__(self, rect: pygame.Rect, options: list[str], font: pygame.font.Font, starting_option: str | None = None) -> None:
        if not options:
            raise ValueError("Dropdown must contain at least one option")

        if starting_option is not None and starting_option not in options:
            raise ValueError("Starting option must be present in options")

        self.rect = rect
        self.options = options
        self.font = font

        self.selected_index = (
            options.index(starting_option)
            if starting_option is not None
            else 0
        )

        self.open = False
        self.hovered = False
        self.hovered_index: int | None = None

        self.background_colour = pygame.Color("#303D4B")
        self.hover_colour = pygame.Color("#415162")
        self.selected_colour = pygame.Color("#384958")
        self.border_colour = pygame.Color("#FFFFFF")
        self.text_colour = pygame.Color("#FFFFFF")

    @property
    def selected(self) -> str:
        """The currently selected option."""

        return self.options[self.selected_index]

    def get_option_rect(self, index: int) -> pygame.Rect:
        """Return the rectangle occupied by an option."""

        return pygame.Rect(
            self.rect.left,
            self.rect.bottom + index * self.rect.height,
            self.rect.width,
            self.rect.height,
        )

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle one Pygame event.

        Returns True when the selected option changes.
        """

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.open:
                self.open = False
            return False

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False

        if self.rect.collidepoint(event.pos):
            self.open = not self.open
            return False

        if self.open:
            for index in range(len(self.options)):
                if self.get_option_rect(index).collidepoint(event.pos):
                    changed = index != self.selected_index

                    self.selected_index = index
                    self.open = False

                    return changed

        # Clicking anywhere outside the dropdown closes it.
        self.open = False
        return False

    def update(self) -> None:
        """Update hover state."""

        mouse_position = pygame.mouse.get_pos()

        self.hovered = self.rect.collidepoint(mouse_position)
        self.hovered_index = None

        if self.open:
            for index in range(len(self.options)):
                if self.get_option_rect(index).collidepoint(mouse_position):
                    self.hovered_index = index
                    break

    def render(self, surface: pygame.Surface) -> None:
        """Draw the dropdown."""

        main_colour = (
            self.hover_colour
            if self.hovered
            else self.background_colour
        )

        self._render_box(surface, self.rect, self.selected, main_colour)
        self._render_arrow(surface)

        if self.open:
            for index, option in enumerate(self.options):
                if index == self.hovered_index:
                    colour = self.hover_colour
                elif index == self.selected_index:
                    colour = self.selected_colour
                else:
                    colour = self.background_colour

                self._render_box(surface, self.get_option_rect(index), option, colour)

    def _render_box(self, surface: pygame.Surface, rect: pygame.Rect, text: str, colour: pygame.Color) -> None:
        pygame.draw.rect(
            surface,
            colour,
            rect,
            border_radius=6,
        )
        pygame.draw.rect(
            surface,
            self.border_colour,
            rect,
            width=2,
            border_radius=6,
        )

        text_surface = self.font.render(
            text,
            True,
            self.text_colour,
        )
        text_rect = text_surface.get_rect(
            midleft=(rect.left + 12, rect.centery)
        )

        surface.blit(text_surface, text_rect)

    def _render_arrow(self, surface: pygame.Surface) -> None:
        centre_x = self.rect.right - 20
        centre_y = self.rect.centery

        if self.open:
            points = [
                (centre_x - 6, centre_y + 3),
                (centre_x + 6, centre_y + 3),
                (centre_x, centre_y - 4),
            ]
        else:
            points = [
                (centre_x - 6, centre_y - 3),
                (centre_x + 6, centre_y - 3),
                (centre_x, centre_y + 4),
            ]

        pygame.draw.polygon(
            surface,
            self.text_colour,
            points,
        )
