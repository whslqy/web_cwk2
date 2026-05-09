"""Website crawling logic."""

from collections import deque
from dataclasses import dataclass
from html.parser import HTMLParser
from time import monotonic, sleep
from typing import Callable
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen

try:
    import requests
except ImportError:  # pragma: no cover - fallback is covered instead.
    requests = None

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover - fallback is covered instead.
    BeautifulSoup = None


@dataclass(slots=True)
class CrawlerConfig:
    """Configuration for the crawler."""

    base_url: str = "https://quotes.toscrape.com/"
    politeness_delay: int = 6
    request_timeout: int = 10


class _HTMLTextParser(HTMLParser):
    """Extract visible text from HTML when BeautifulSoup is unavailable."""

    def __init__(self) -> None:
        super().__init__()
        self._ignored_tag_depth = 0
        self._text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._ignored_tag_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._ignored_tag_depth > 0:
            self._ignored_tag_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._ignored_tag_depth == 0:
            cleaned = data.strip()
            if cleaned:
                self._text_parts.append(cleaned)

    def get_text(self) -> str:
        return " ".join(self._text_parts)


class _HTMLLinkParser(HTMLParser):
    """Extract links from HTML when BeautifulSoup is unavailable."""

    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return

        href = dict(attrs).get("href")
        if not href:
            return

        self.links.append(urljoin(self.base_url, href))


class Crawler:
    """Initial crawler implementation for the target website."""

    def __init__(
        self,
        config: CrawlerConfig | None = None,
        session: object | None = None,
        sleep_func: Callable[[float], None] = sleep,
        time_func: Callable[[], float] = monotonic,
    ) -> None:
        self.config = config or CrawlerConfig()
        self.session = session
        self.sleep_func = sleep_func
        self.time_func = time_func
        self._last_request_time: float | None = None

    def crawl(self) -> list[dict[str, object]]:
        """Fetch and parse all reachable same-site pages."""
        pages: list[dict[str, object]] = []
        pending_urls = deque([self.normalise_url(self.config.base_url)])
        visited_urls: set[str] = set()

        while pending_urls:
            current_url = pending_urls.popleft()
            if current_url in visited_urls:
                continue

            html = self.fetch_page(current_url)
            page = self.parse_page(current_url, html)
            pages.append(page)
            visited_urls.add(current_url)

            for link in page["links"]:
                normalised_link = self.normalise_url(str(link))
                if normalised_link not in visited_urls:
                    pending_urls.append(normalised_link)

        return pages

    def parse_page(self, url: str, html: str) -> dict[str, object]:
        """Build a page record from raw HTML."""
        return {
            "url": self.normalise_url(url),
            "title": self.extract_title(html),
            "words": self.extract_words(html),
            "links": self.extract_links(html, url),
        }

    def fetch_page(self, url: str) -> str:
        """Return HTML for a single page request."""
        self._wait_if_needed()

        if self.session is not None:
            response = self.session.get(url, timeout=self.config.request_timeout)
            response.raise_for_status()
            html = response.text
        elif requests is not None:
            response = requests.get(url, timeout=self.config.request_timeout)
            response.raise_for_status()
            html = response.text
        else:
            with urlopen(url, timeout=self.config.request_timeout) as response:
                html = response.read().decode("utf-8", errors="ignore")

        self._last_request_time = self.time_func()
        return html

    def normalise_url(self, url: str) -> str:
        """Normalise a URL so crawl deduplication is stable."""
        parsed = urlparse(urljoin(self.config.base_url, url))
        path = parsed.path or "/"
        return parsed._replace(fragment="", params="", query="", path=path).geturl()

    def extract_title(self, html: str) -> str:
        """Extract the page title."""
        if BeautifulSoup is not None:
            soup = BeautifulSoup(html, "html.parser")
            return soup.title.get_text(strip=True) if soup.title else ""

        parser = _HTMLTextParser()
        parser.feed(f"<title>{html.split('<title>', 1)[1].split('</title>', 1)[0]}</title>") if (
            "<title>" in html and "</title>" in html
        ) else None
        return parser.get_text()

    def extract_words(self, html: str) -> str:
        """Extract visible text from a page."""
        if BeautifulSoup is not None:
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            return " ".join(soup.get_text(" ", strip=True).split())

        parser = _HTMLTextParser()
        parser.feed(html)
        return " ".join(parser.get_text().split())

    def extract_links(self, html: str, page_url: str) -> list[str]:
        """Extract same-site links from the current page."""
        base_netloc = urlparse(self.config.base_url).netloc

        if BeautifulSoup is not None:
            soup = BeautifulSoup(html, "html.parser")
            links = [
                urljoin(page_url, element["href"])
                for element in soup.select("a[href]")
            ]
        else:
            parser = _HTMLLinkParser(page_url)
            parser.feed(html)
            links = parser.links

        unique_links: list[str] = []
        seen: set[str] = set()
        for link in links:
            normalised_link = self.normalise_url(link)
            parsed = urlparse(normalised_link)
            if parsed.netloc != base_netloc:
                continue
            if normalised_link in seen:
                continue
            seen.add(normalised_link)
            unique_links.append(normalised_link)

        return unique_links

    def _wait_if_needed(self) -> None:
        """Respect the politeness window between successive requests."""
        if self._last_request_time is None:
            return

        elapsed = self.time_func() - self._last_request_time
        remaining = self.config.politeness_delay - elapsed
        if remaining > 0:
            self.sleep_func(remaining)
