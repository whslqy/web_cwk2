from src.main import HELP_TEXT, parse_command, run_command


class FakeEngine:
    def __init__(self) -> None:
        self.actions: list[tuple[str, str | None]] = []

    def build(self) -> dict:
        self.actions.append(("build", None))
        return {"metadata": {"page_count": 2, "indexed_terms": 5}, "index": {}}

    def load(self) -> dict:
        self.actions.append(("load", None))
        return {"metadata": {"page_count": 2, "indexed_terms": 5}, "index": {}}

    def print_word(self, word: str) -> dict:
        self.actions.append(("print", word))
        return {"word": word}

    def find(self, query: str) -> list[str]:
        self.actions.append(("find", query))
        return [query]


def test_parse_command_handles_find_query() -> None:
    command = parse_command("find good friends")
    assert command.name == "find"
    assert command.argument == "good friends"


def test_parse_command_rejects_print_with_multiple_words() -> None:
    try:
        parse_command("print too many")
    except ValueError as error:
        assert str(error) == "'print' requires exactly one word."
    else:
        raise AssertionError("Expected ValueError for invalid print command.")


def test_run_command_executes_build() -> None:
    engine = FakeEngine()
    outputs: list[object] = []

    should_continue = run_command(engine, "build", outputs.append)

    assert should_continue is True
    assert engine.actions == [("build", None)]
    assert outputs == [
        "Building index. Progress will be shown below and requests wait 6 seconds between pages.",
        "Index built. Pages: 2, terms: 5.",
    ]


def test_run_command_executes_print() -> None:
    engine = FakeEngine()
    outputs: list[object] = []

    should_continue = run_command(engine, "print nonsense", outputs.append)

    assert should_continue is True
    assert engine.actions == [("print", "nonsense")]
    assert outputs == ['{\n  "word": "nonsense"\n}']


def test_run_command_outputs_help_text() -> None:
    engine = FakeEngine()
    outputs: list[object] = []

    should_continue = run_command(engine, "help", outputs.append)

    assert should_continue is True
    assert engine.actions == []
    assert outputs == [HELP_TEXT.strip()]


def test_run_command_reports_no_results_for_find() -> None:
    engine = FakeEngine()
    outputs: list[object] = []
    engine.find = lambda query: []

    should_continue = run_command(engine, "find missing", outputs.append)

    assert should_continue is True
    assert outputs == ["No pages found for query: missing"]


def test_run_command_stops_shell_for_exit() -> None:
    engine = FakeEngine()
    outputs: list[object] = []

    should_continue = run_command(engine, "exit", outputs.append)

    assert should_continue is False
    assert outputs == ["Exiting."]
