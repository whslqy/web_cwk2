# Search Engine Tool

Coursework 2 project for `COMP/XJCO3011`.

## Project Overview

This project implements a small search engine for
`https://quotes.toscrape.com/`. It:

- crawls the target website while respecting the politeness window
- extracts visible page text and same-site links
- builds a case-insensitive inverted index with word frequency and positions
- saves and loads the compiled index from disk
- supports `print` and `find` commands through a command-line shell

## Project Structure

- `src/crawler.py`: crawling and page parsing
- `src/indexer.py`: tokenisation and inverted index logic
- `src/search.py`: build, load, and query orchestration
- `src/main.py`: interactive shell
- `tests/`: module-level tests
- `data/`: generated index file

## Setup

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Usage

Start the shell:

```powershell
.\.venv\Scripts\python.exe -m src.main
```

Available commands:

- `build`
- `load`
- `print <word>`
- `find <query>`
- `help`
- `exit`

Example session:

```text
> build
> load
> print nonsense
> find good friends
```

## Testing

If `pytest` is installed in the virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Dependencies

- `requests`
- `beautifulsoup4`
- `pytest`
