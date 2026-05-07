from src.indexer import InvertedIndex


def test_normalise_word_is_case_insensitive() -> None:
    assert InvertedIndex.normalise_word(" Good ") == "good"


def test_add_page_tracks_frequency_and_positions() -> None:
    index = InvertedIndex()
    index.add_page("page-1", ["good", "friends", "good"])

    assert index.data["good"]["page-1"]["frequency"] == 2
    assert index.data["good"]["page-1"]["positions"] == [0, 2]

