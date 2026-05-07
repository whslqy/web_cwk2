"""Website crawling logic."""

from dataclasses import dataclass


@dataclass(slots=True)
class CrawlerConfig:
    """Configuration for the crawler."""

    base_url: str = "https://quotes.toscrape.com/"
    politeness_delay: int = 6


class Crawler:
    """Minimal crawler skeleton."""

    def __init__(self, config: CrawlerConfig | None = None) -> None:
        self.config = config or CrawlerConfig()

    def crawl(self) -> list[dict[str, str]]:
        """Return crawled page data.

        TODO:
        - request pages from the target website
        - wait at least 6 seconds between requests
        - extract page text and metadata
        """
        return []

