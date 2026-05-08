from src.main import HELP_TEXT, parse_command, run_command


class FakeEngine:
    def __init__(self) -> None:
        self.actions: list[tuple[str, str | None]] = []

    def build(self) -> None:
        self.actions.append(("build", None))

    def load(self) -> dict:
        self.actions.append(("load", None))
        return {}

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
    assert outputs == ["Index built."]


def test_run_command_executes_print() -> None:
    engine = FakeEngine()
    outputs: list[object] = []

    should_continue = run_command(engine, "print nonsense", outputs.append)

    assert should_continue is True
    assert engine.actions == [("print", "nonsense")]
    assert outputs == [{"word": "nonsense"}]


def test_run_command_outputs_help_text() -> None:
    engine = FakeEngine()
    outputs: list[object] = []

    should_continue = run_command(engine, "help", outputs.append)

    assert should_continue is True
    assert engine.actions == []
    assert outputs == [HELP_TEXT.strip()]


def test_run_command_stops_shell_for_exit() -> None:
    engine = FakeEngine()
    outputs: list[object] = []

    should_continue = run_command(engine, "exit", outputs.append)

    assert should_continue is False
    assert outputs == ["Exiting."]
