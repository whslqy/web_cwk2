from pathlib import Path

from src.search import SearchEngine


def test_print_word_returns_empty_dict_for_missing_word(tmp_path: Path) -> None:
    engine = SearchEngine(index_path=tmp_path / "index.json")
    assert engine.print_word("missing") == {}


def test_find_returns_pages_matching_all_terms(tmp_path: Path) -> None:
    engine = SearchEngine(index_path=tmp_path / "index.json")
    engine.index.add_page("page-1", ["good", "friends"])
    engine.index.add_page("page-2", ["good"])

    assert engine.find("good friends") == ["page-1"]

