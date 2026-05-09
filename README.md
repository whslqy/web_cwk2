# Search Engine Tool

Coursework 2 skeleton for `COMP/XJCO3011`.

## Planned Structure

- `src/crawler.py`: crawl the target website with a 6-second politeness window
- `src/indexer.py`: build and store the inverted index
- `src/search.py`: load the index and execute search queries
- `src/main.py`: command-line shell for `build`, `load`, `print`, and `find`
- `tests/`: unit tests for each module
- `data/`: generated index file

## Setup

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run

```powershell
.\.venv\Scripts\python.exe -m src.main
```

## Current Status

This repository currently contains a minimal CLI shell and an initial
homepage crawler.
