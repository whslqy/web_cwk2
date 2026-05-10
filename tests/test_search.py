from pathlib import Path

from src.crawler import Crawler
from src.search import SearchEngine


class FakeCrawler(Crawler):
    def __init__(self, pages: list[dict[str, object]]) -> None:
        self.pages = pages

    def crawl(self) -> list[dict[str, object]]:
        return self.pages


def test_print_word_returns_empty_dict_for_missing_word(tmp_path: Path) -> None:
    engine = SearchEngine(index_path=tmp_path / "index.json")
    assert engine.print_word("missing") == {}


def test_find_returns_pages_matching_all_terms(tmp_path: Path) -> None:
    engine = SearchEngine(index_path=tmp_path / "index.json")
    engine.index.add_page("page-1", ["good", "friends"])
    engine.index.add_page("page-2", ["good"])

    assert engine.find("good friends") == ["page-1"]


def test_find_handles_punctuation_and_case_insensitive_queries(tmp_path: Path) -> None:
    engine = SearchEngine(index_path=tmp_path / "index.json")
    engine.index.add_page("page-1", "Good friends, good books.")
    engine.index.add_page("page-2", "Good habits.")

    assert engine.find("GOOD, friends!") == ["page-1"]


def test_build_writes_payload_and_load_restores_index(tmp_path: Path) -> None:
    pages = [
        {"url": "page-1", "words": "Good friends and good books"},
        {"url": "page-2", "words": "Indifference is expensive"},
    ]
    index_path = tmp_path / "index.json"
    engine = SearchEngine(index_path=index_path, crawler=FakeCrawler(pages))

    payload = engine.build()

    assert payload["metadata"]["page_count"] == 2
    assert "good" in payload["index"]
    assert index_path.exists()

    loaded_engine = SearchEngine(index_path=index_path)
    loaded_payload = loaded_engine.load()

    assert loaded_payload["metadata"]["indexed_terms"] >= 1
    assert loaded_engine.print_word("good")["page-1"]["frequency"] == 2


def test_find_returns_empty_list_for_missing_term(tmp_path: Path) -> None:
    engine = SearchEngine(index_path=tmp_path / "index.json")
    engine.index.add_page("page-1", "good friends")

    assert engine.find("missing friends") == []
