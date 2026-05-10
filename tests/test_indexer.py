from src.indexer import InvertedIndex


def test_normalise_word_is_case_insensitive() -> None:
    assert InvertedIndex.normalise_word(" Good ") == "good"


def test_tokenise_strips_punctuation_and_normalises_case() -> None:
    assert InvertedIndex.tokenise("Good friends, GOOD times!") == [
        "good",
        "friends",
        "good",
        "times",
    ]


def test_add_page_tracks_frequency_and_positions() -> None:
    index = InvertedIndex()
    index.add_page("page-1", ["good", "friends", "good"])

    assert index.data["good"]["page-1"]["frequency"] == 2
    assert index.data["good"]["page-1"]["positions"] == [0, 2]


def test_add_page_accepts_raw_text() -> None:
    index = InvertedIndex()
    index.add_page("page-1", "Good friends, good books.")

    assert index.data["good"]["page-1"]["frequency"] == 2
    assert index.data["books"]["page-1"]["positions"] == [3]
