import pygame


class ScrollableTextBox:
    """
        Scrollable text box UI element
        Provide a multi line string and the user can read the text whilst scrolling
    """

    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font, *, padding: int = 12, scroll_lines: int = 3) -> None:
        self.rect = rect
        self.font = font
        self.padding = padding
        self.scroll_lines = scroll_lines

        self.background_colour = pygame.Color("#202732")
        self.border_colour = pygame.Color("#77818C")
        self.text_colour = pygame.Color("#FFFFFF")
        self.scrollbar_colour = pygame.Color("#303D4B")
        self.scrollbar_thumb_colour = pygame.Color("#77818C")
        self.scrollbar_hover_colour = pygame.Color("#A0A8B0")

        self.scrollbar_width = 10
        self.scrollbar_gap = 6

        self.text = ""
        self.lines: list[str] = []
        self.scroll_y = 0
        self.hovered = False
        self.scrollbar_hovered = False

        self.set_text(text)

    @property
    def content_rect(self) -> pygame.Rect:
        """The visible area in which text is rendered."""

        return pygame.Rect(
            self.rect.left + self.padding,
            self.rect.top + self.padding,
            self.rect.width
            - self.padding * 2
            - self.scrollbar_width
            - self.scrollbar_gap,
            self.rect.height - self.padding * 2,
        )

    @property
    def content_height(self) -> int:
        return len(self.lines) * self.font.get_linesize()

    @property
    def max_scroll(self) -> int:
        return max(
            0,
            self.content_height - self.content_rect.height,
        )

    def set_text(self, text: str) -> None:
        """Replace the displayed text and recalculate wrapping."""

        self.text = text
        self.lines = self._wrap_text(text)
        self.scroll_y = min(self.scroll_y, self.max_scroll)

    def scroll_to_top(self) -> None:
        self.scroll_y = 0

    def scroll_to_bottom(self) -> None:
        self.scroll_y = self.max_scroll

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle scrolling input while the mouse is over the box."""

        mouse_position = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(mouse_position):
                distance = self.font.get_linesize() * self.scroll_lines
                self.scroll_y -= event.y * distance
                self._clamp_scroll()

        elif event.type == pygame.KEYDOWN and self.hovered:
            line_height = self.font.get_linesize()

            if event.key == pygame.K_UP:
                self.scroll_y -= line_height

            elif event.key == pygame.K_DOWN:
                self.scroll_y += line_height

            elif event.key == pygame.K_PAGEUP:
                self.scroll_y -= self.content_rect.height

            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_y += self.content_rect.height

            elif event.key == pygame.K_HOME:
                self.scroll_to_top()

            elif event.key == pygame.K_END:
                self.scroll_to_bottom()

            self._clamp_scroll()

    def update(self) -> None:
        """Update hover state."""

        mouse_position = pygame.mouse.get_pos()

        self.hovered = self.rect.collidepoint(mouse_position)

        thumb_rect = self._get_scrollbar_thumb_rect()
        self.scrollbar_hovered = thumb_rect is not None and thumb_rect.collidepoint(mouse_position)

    def render(self, surface: pygame.Surface) -> None:
        """Render the text box, visible text and scrollbar."""

        pygame.draw.rect(
            surface,
            self.background_colour,
            self.rect,
            border_radius=7,
        )
        pygame.draw.rect(
            surface,
            self.border_colour,
            self.rect,
            width=2,
            border_radius=7,
        )

        content_rect = self.content_rect

        # Keep text inside the content area.
        previous_clip = surface.get_clip()
        surface.set_clip(content_rect)

        line_height = self.font.get_linesize()

        # Skip lines above the visible area.
        first_visible_line = self.scroll_y // line_height
        offset_y = -(self.scroll_y % line_height)

        y = content_rect.top + offset_y

        for line in self.lines[first_visible_line:]:
            if y >= content_rect.bottom:
                break

            text_surface = self.font.render(line, True, self.text_colour)
            surface.blit(text_surface, (content_rect.left, y))

            y += line_height

        surface.set_clip(previous_clip)

        self._render_scrollbar(surface)

    def _wrap_text(self, text: str) -> list[str]:
        """Wrap text while preserving explicit newlines."""

        maximum_width = self.content_rect.width
        wrapped_lines: list[str] = []

        for paragraph in text.splitlines():
            if paragraph == "":
                wrapped_lines.append("")
                continue

            words = paragraph.split()
            current_line = ""

            for word in words:
                candidate = word if not current_line else f"{current_line} {word}"

                if self.font.size(candidate)[0] <= maximum_width:
                    current_line = candidate
                    continue

                if current_line:
                    wrapped_lines.append(current_line)
                    current_line = ""

                # Split individual words that are wider than the box.
                if self.font.size(word)[0] > maximum_width:
                    pieces = self._split_long_word(word, maximum_width)
                    wrapped_lines.extend(pieces[:-1])
                    current_line = pieces[-1]
                else:
                    current_line = word

            if current_line:
                wrapped_lines.append(current_line)

        # Ensure an empty text box still has one renderable line.
        return wrapped_lines or [""]

    def _split_long_word(self, word: str, maximum_width: int) -> list[str]:
        pieces: list[str] = []
        current_piece = ""

        for character in word:
            candidate = current_piece + character

            if (current_piece and self.font.size(candidate)[0] > maximum_width):
                pieces.append(current_piece)
                current_piece = character
            else:
                current_piece = candidate

        if current_piece:
            pieces.append(current_piece)

        return pieces

    def _get_scrollbar_track_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.rect.right
            - self.padding
            - self.scrollbar_width,
            self.rect.top + self.padding,
            self.scrollbar_width,
            self.rect.height - self.padding * 2,
        )

    def _get_scrollbar_thumb_rect(self) -> pygame.Rect | None:
        if self.max_scroll == 0:
            return None

        track = self._get_scrollbar_track_rect()

        visible_fraction = self.content_rect.height / self.content_height

        thumb_height = max(20, int(track.height * visible_fraction))

        available_travel = track.height - thumb_height
        scroll_fraction = self.scroll_y / self.max_scroll

        thumb_y = track.top + int(available_travel * scroll_fraction)

        return pygame.Rect(
            track.left,
            thumb_y,
            track.width,
            thumb_height,
        )

    def _render_scrollbar(self, surface: pygame.Surface) -> None:
        thumb = self._get_scrollbar_thumb_rect()

        if thumb is None:
            return

        track = self._get_scrollbar_track_rect()

        pygame.draw.rect(surface, self.scrollbar_colour, track, border_radius=5)

        thumb_colour = (
            self.scrollbar_hover_colour
            if self.scrollbar_hovered
            else self.scrollbar_thumb_colour
        )

        pygame.draw.rect(surface, thumb_colour, thumb, border_radius=5)

    def _clamp_scroll(self) -> None:
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))
