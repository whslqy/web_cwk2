# Search Engine Tool

Coursework 2 project for `COMP/XJCO3011`.

## Project Overview

This project implements a small search engine for
`https://quotes.toscrape.com/`. It:

- crawls the target website while respecting the politeness window
- crawls reachable same-site pages starting from the base URL
- extracts visible page text and same-site links
- builds a case-insensitive inverted index during crawling
- stores word frequency and positions for each page
- skips failed pages and records them in the build summary
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

- `build`: crawl the site and save the compiled index to `data/index.json`
- `load`: load the saved index file from disk
- `print <word>`: show the posting list for a single term
- `find <query>`: return pages that match one or more query terms
- `help`
- `exit`

Search is case-insensitive, so queries such as `life`, `Life`, and `LIFE`
are treated as the same word.

Example session:

```text
> build
> load
> print nonsense
> find good friends
```

## Testing

Run the automated tests with:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Dependencies

- `requests`
- `beautifulsoup4`
- `pytest`
