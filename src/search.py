"""Search engine orchestration."""

import json
from pathlib import Path

from src.crawler import Crawler
from src.indexer import InvertedIndex


class SearchEngine:
    """Minimal search engine skeleton."""

    def __init__(self, index_path: Path | None = None) -> None:
        self.index_path = index_path or Path("data/index.json")
        self.index = InvertedIndex()

    def build(self) -> None:
        """Crawl the site and write the compiled index to disk."""
        crawler = Crawler()
        pages = crawler.crawl()
        self.index = InvertedIndex()

        for page in pages:
            url = page.get("url", "")
            words = page.get("words", "").split()
            self.index.add_page(url, words)

        self.index_path.write_text(
            json.dumps(self.index.to_dict(), indent=2),
            encoding="utf-8",
        )

    def load(self) -> dict:
        """Load the stored index from disk."""
        data = json.loads(self.index_path.read_text(encoding="utf-8"))
        self.index.data = data
        return data

    def print_word(self, word: str) -> dict:
        """Return the posting list for a single word."""
        return self.index.data.get(word.strip().lower(), {})

    def find(self, query: str) -> list[str]:
        """Return pages containing all words in a query."""
        terms = [term.strip().lower() for term in query.split() if term.strip()]
        if not terms:
            return []

        results: list[set[str]] = []
        for term in terms:
            matches = set(self.index.data.get(term, {}).keys())
            results.append(matches)

        if not results:
            return []

        return sorted(set.intersection(*results))

