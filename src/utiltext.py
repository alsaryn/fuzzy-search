"""Provide text translation utilities."""

from uwuipy import Uwuipy


class _TextTranslation:
    """Provide text translation utilities."""

    def __init__(self):
        """Initialize progress bar."""
        self.uwu = None

    def set_curse_level(self, level: int) -> None:
        """Set level of uwu-ified text."""
        if level == 0:
            # no change
            self.uwu = None
        elif level == 1:
            # Just text translation
            self.uwu = Uwuipy(None, 0.0, 0.0, 0.0, 0, False, 1)
        elif level == 2:
            # more nya-nya, faces, stutters, actions
            self.uwu = Uwuipy(None, 0.1, 0.05, 0.075, 0.5, False, 2)
        else:
            # Awful
            self.uwu = Uwuipy(None, 0.3, 0.3, 0.3, 1, True, 4)
            self.uwu = Uwuipy()

    def text(self, text: str) -> str:
        """Get the uwu-translated version of a string."""
        if self.uwu:
            return self.uwu.uwuify(text)
        return text


# Shared instance of class
translate = _TextTranslation()
