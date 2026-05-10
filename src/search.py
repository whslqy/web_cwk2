"""Search engine orchestration."""

import json
from pathlib import Path
from typing import Any

from src.crawler import Crawler
from src.indexer import InvertedIndex


class SearchEngine:
    """Search engine orchestration for crawling, indexing, and querying."""

    def __init__(
        self,
        index_path: Path | None = None,
        crawler: Crawler | None = None,
    ) -> None:
        self.index_path = index_path or Path("data/index.json")
        self.crawler = crawler or Crawler()
        self.index = InvertedIndex()
        self.metadata: dict[str, Any] = {"page_count": 0, "indexed_terms": 0}

    def build(self) -> dict[str, Any]:
        """Crawl the site and write the compiled index to disk."""
        pages = self.crawler.crawl()
        self.index = InvertedIndex()

        for page in pages:
            url = str(page.get("url", "")).strip()
            text = str(page.get("words", ""))
            if not url:
                continue
            self.index.add_page(url, text)

        self.metadata = {
            "page_count": len(pages),
            "indexed_terms": len(self.index.data),
        }
        payload = {
            "metadata": self.metadata,
            "index": self.index.to_dict(),
        }
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.index_path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )
        return payload

    def load(self) -> dict[str, Any]:
        """Load the stored index from disk."""
        payload = json.loads(self.index_path.read_text(encoding="utf-8"))

        if "index" in payload:
            self.metadata = payload.get("metadata", self.metadata)
            self.index = InvertedIndex.from_dict(payload["index"])
            return payload

        self.index = InvertedIndex.from_dict(payload)
        self.metadata = {
            "page_count": sum(
                1
                for _ in {
                    page_url
                    for postings in self.index.data.values()
                    for page_url in postings.keys()
                }
            ),
            "indexed_terms": len(self.index.data),
        }
        return {"metadata": self.metadata, "index": self.index.to_dict()}

    def print_word(self, word: str) -> dict[str, dict[str, list[int] | int]]:
        """Return the posting list for a single word."""
        return self.index.get_postings(word)

    def find(self, query: str) -> list[str]:
        """Return pages containing all words in a query."""
        terms = InvertedIndex.tokenise(query)
        if not terms:
            return []

        results: list[set[str]] = []
        for term in terms:
            matches = set(self.index.get_postings(term).keys())
            if not matches:
                return []
            results.append(matches)

        shared_urls = set.intersection(*results)
        return sorted(
            shared_urls,
            key=lambda url: (-self._score_url(url, terms), url),
        )

    def _score_url(self, url: str, terms: list[str]) -> int:
        """Simple ranking based on total frequency across query terms."""
        return sum(
            int(self.index.get_postings(term).get(url, {}).get("frequency", 0))
            for term in terms
        )
