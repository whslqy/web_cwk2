"""Inverted index structures and helpers."""

from collections import defaultdict


class InvertedIndex:
    """Minimal inverted index skeleton."""

    def __init__(self) -> None:
        self.data: dict[str, dict[str, dict[str, list[int] | int]]] = defaultdict(dict)

    @staticmethod
    def normalise_word(word: str) -> str:
        """Normalise a word for case-insensitive search."""
        return word.strip().lower()

    def add_page(self, page_url: str, words: list[str]) -> None:
        """Populate the index from a page word list."""
        for position, word in enumerate(words):
            normalised = self.normalise_word(word)
            if not normalised:
                continue

            entry = self.data.setdefault(normalised, {}).setdefault(
                page_url,
                {"frequency": 0, "positions": []},
            )
            entry["frequency"] += 1
            entry["positions"].append(position)

    def to_dict(self) -> dict[str, dict[str, dict[str, list[int] | int]]]:
        """Convert the index into a serialisable structure."""
        return dict(self.data)

