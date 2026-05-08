"""Command-line shell for the search engine tool."""

from dataclasses import dataclass
from typing import Callable

from src.search import SearchEngine

HELP_TEXT = """Available commands:
- build
- load
- print <word>
- find <query>
- help
- exit
"""


@dataclass(slots=True)
class Command:
    """Parsed command-line input."""

    name: str
    argument: str = ""


def parse_command(raw_command: str) -> Command:
    """Parse a shell command into a command name and optional argument."""
    cleaned = raw_command.strip()
    if not cleaned:
        raise ValueError("Please enter a command.")

    parts = cleaned.split(maxsplit=1)
    name = parts[0].lower()
    argument = parts[1].strip() if len(parts) > 1 else ""

    if name in {"build", "load", "help", "exit", "quit"}:
        if argument:
            raise ValueError(f"'{name}' does not take any arguments.")
        return Command(name=name)

    if name == "print":
        if not argument:
            raise ValueError("'print' requires a single word.")
        if len(argument.split()) != 1:
            raise ValueError("'print' requires exactly one word.")
        return Command(name=name, argument=argument)

    if name == "find":
        if not argument:
            raise ValueError("'find' requires a query.")
        return Command(name=name, argument=argument)

    raise ValueError("Unknown command.")


def run_command(
    engine: SearchEngine,
    raw_command: str,
    output: Callable[[object], None] = print,
) -> bool:
    """Execute a raw shell command.

    Returns False when the shell should exit.
    """
    try:
        command = parse_command(raw_command)
    except ValueError as error:
        output(error)
        return True

    if command.name in {"exit", "quit"}:
        output("Exiting.")
        return False

    if command.name == "help":
        output(HELP_TEXT.strip())
        return True

    if command.name == "build":
        engine.build()
        output("Index built.")
        return True

    if command.name == "load":
        try:
            engine.load()
        except FileNotFoundError:
            output("Index file not found. Run build first.")
        else:
            output("Index loaded.")
        return True

    if command.name == "print":
        output(engine.print_word(command.argument))
        return True

    output(engine.find(command.argument))
    return True


def main() -> None:
    """Run the interactive shell."""
    engine = SearchEngine()

    while True:
        try:
            raw_command = input("> ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not run_command(engine, raw_command):
            break


if __name__ == "__main__":
    main()
