"""Inverted index structures and helpers."""

from collections import defaultdict
import re

WORD_PATTERN = re.compile(r"[A-Za-z0-9']+")


class InvertedIndex:
    """Case-insensitive inverted index with frequency and position data."""

    def __init__(
        self,
        data: dict[str, dict[str, dict[str, list[int] | int]]] | None = None,
    ) -> None:
        self.data: dict[str, dict[str, dict[str, list[int] | int]]] = defaultdict(dict)
        if data:
            for word, postings in data.items():
                self.data[word] = postings

    @staticmethod
    def normalise_word(word: str) -> str:
        """Normalise a word for case-insensitive search."""
        return word.strip().lower()

    @classmethod
    def tokenise(cls, text: str) -> list[str]:
        """Extract case-insensitive word tokens from text."""
        return [cls.normalise_word(match) for match in WORD_PATTERN.findall(text)]

    def add_page(self, page_url: str, words: list[str] | str) -> None:
        """Populate the index from a page word list or raw text."""
        tokens = self.tokenise(words) if isinstance(words, str) else [
            self.normalise_word(word)
            for word in words
            if self.normalise_word(word)
        ]

        for position, word in enumerate(tokens):
            entry = self.data.setdefault(word, {}).setdefault(
                page_url,
                {"frequency": 0, "positions": []},
            )
            entry["frequency"] += 1
            entry["positions"].append(position)

    def get_postings(self, word: str) -> dict[str, dict[str, list[int] | int]]:
        """Return the posting list for a single word."""
        return self.data.get(self.normalise_word(word), {})

    def to_dict(self) -> dict[str, dict[str, dict[str, list[int] | int]]]:
        """Convert the index into a serialisable structure."""
        return {word: postings for word, postings in self.data.items()}

    @classmethod
    def from_dict(
        cls,
        data: dict[str, dict[str, dict[str, list[int] | int]]],
    ) -> "InvertedIndex":
        """Create an inverted index from previously stored data."""
        return cls(data=data)
