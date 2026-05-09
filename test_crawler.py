from src.crawler import Crawler, CrawlerConfig


class FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text

    def raise_for_status(self) -> None:
        return None


class FakeSession:
    def __init__(self, html: str | None = None, pages: dict[str, str] | None = None) -> None:
        self.html = html
        self.pages = pages or {}
        self.calls: list[tuple[str, int]] = []

    def get(self, url: str, timeout: int) -> FakeResponse:
        self.calls.append((url, timeout))
        if self.pages:
            return FakeResponse(self.pages[url])
        if self.html is None:
            raise KeyError(url)
        return FakeResponse(self.html)


def test_crawler_uses_default_config() -> None:
    crawler = Crawler()
    assert crawler.config.base_url == "https://quotes.toscrape.com/"
    assert crawler.config.politeness_delay == 6


def test_crawler_accepts_custom_config() -> None:
    config = CrawlerConfig(base_url="https://example.com", politeness_delay=10)
    crawler = Crawler(config)
    assert crawler.config == config


def test_crawler_fetches_homepage_content() -> None:
    html = """
    <html>
      <head><title>Quotes to Scrape</title></head>
      <body>
        <div class="quote">First quote here.</div>
        <a href="/page/2/">Next</a>
      </body>
    </html>
    """
    session = FakeSession(html)
    crawler = Crawler(session=session)

    pages = crawler.crawl()

    assert session.calls == [("https://quotes.toscrape.com/", 10)]
    assert len(pages) == 1
    assert pages[0]["url"] == "https://quotes.toscrape.com/"
    assert pages[0]["title"] == "Quotes to Scrape"
    assert "First quote here." in pages[0]["words"]
    assert pages[0]["links"] == ["https://quotes.toscrape.com/page/2/"]


def test_crawler_follows_same_site_links_without_recrawling() -> None:
    pages = {
        "https://quotes.toscrape.com/": """
        <html>
          <head><title>Home</title></head>
          <body>
            <div>Home quote.</div>
            <a href="/page/2/">Page 2</a>
            <a href="/page/2/#top">Page 2 duplicate</a>
          </body>
        </html>
        """,
        "https://quotes.toscrape.com/page/2/": """
        <html>
          <head><title>Page 2</title></head>
          <body>
            <div>Second page quote.</div>
            <a href="/">Home</a>
            <a href="https://example.com/">External</a>
          </body>
        </html>
        """,
    }
    session = FakeSession(pages=pages)
    crawler = Crawler(session=session)

    crawled_pages = crawler.crawl()

    assert [page["url"] for page in crawled_pages] == [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
    ]
    assert session.calls == [
        ("https://quotes.toscrape.com/", 10),
        ("https://quotes.toscrape.com/page/2/", 10),
    ]
    assert crawled_pages[1]["links"] == ["https://quotes.toscrape.com/"]


def test_crawler_respects_politeness_window_between_requests() -> None:
    session = FakeSession("<html><body>content</body></html>")
    sleep_calls: list[float] = []
    time_values = iter([0.0, 1.0, 2.0])
    crawler = Crawler(
        session=session,
        sleep_func=sleep_calls.append,
        time_func=lambda: next(time_values),
    )

    crawler.fetch_page("https://quotes.toscrape.com/")
    crawler.fetch_page("https://quotes.toscrape.com/page/2/")

    assert sleep_calls == [5.0]
