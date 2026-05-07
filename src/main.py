"""Command-line shell for the search engine tool."""

from src.search import SearchEngine


def main() -> None:
    engine = SearchEngine()

    while True:
        raw_command = input("> ").strip()
        if not raw_command:
            print("Please enter a command.")
            continue

        if raw_command in {"exit", "quit"}:
            print("Exiting.")
            break

        if raw_command == "build":
            engine.build()
            print("Index built.")
            continue

        if raw_command == "load":
            try:
                engine.load()
            except FileNotFoundError:
                print("Index file not found. Run build first.")
            else:
                print("Index loaded.")
            continue

        if raw_command.startswith("print "):
            _, word = raw_command.split(" ", 1)
            print(engine.print_word(word))
            continue

        if raw_command.startswith("find "):
            _, query = raw_command.split(" ", 1)
            print(engine.find(query))
            continue

        print("Unknown command.")


if __name__ == "__main__":
    main()

