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
            page = self.pages[url]
            if isinstance(page, Exception):
                raise page
            return FakeResponse(page)
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
    assert pages[0]["links"] == []


def test_crawler_follows_same_site_links_without_recrawling() -> None:
    pages = {
        "https://quotes.toscrape.com/": """
        <html>
          <head><title>Home</title></head>
          <body>
            <div>Home quote.</div>
            <a href="/page/2/">Page 2</a>
            <a href="/page/2/#top">Page 2 duplicate</a>
            <a href="/author/Albert-Einstein/">Author</a>
          </body>
        </html>
        """,
        "https://quotes.toscrape.com/page/2/": """
        <html>
          <head><title>Page 2</title></head>
          <body>
            <div>Second page quote.</div>
            <a href="/">Home</a>
            <a href="/author/Albert-Einstein/">Author</a>
            <a href="https://example.com/">External</a>
          </body>
        </html>
        """,
        "https://quotes.toscrape.com/author/Albert-Einstein/": """
        <html>
          <head><title>Albert Einstein</title></head>
          <body>
            <div>Author page.</div>
            <a href="/page/2/">Back to page 2</a>
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
        "https://quotes.toscrape.com/author/Albert-Einstein/",
    ]
    assert session.calls == [
        ("https://quotes.toscrape.com/", 10),
        ("https://quotes.toscrape.com/page/2/", 10),
        ("https://quotes.toscrape.com/author/Albert-Einstein/", 10),
    ]
    assert crawled_pages[1]["links"] == [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/author/Albert-Einstein/",
    ]


def test_should_visit_url_accepts_same_site_pages_only() -> None:
    crawler = Crawler()

    assert crawler.should_visit_url("https://quotes.toscrape.com/")
    assert crawler.should_visit_url("https://quotes.toscrape.com/page/3/")
    assert crawler.should_visit_url("https://quotes.toscrape.com/author/Albert-Einstein/")
    assert crawler.should_visit_url("https://quotes.toscrape.com/tag/love/")
    assert crawler.should_visit_url("https://quotes.toscrape.com/login")
    assert not crawler.should_visit_url("https://example.com/page/3/")


def test_crawler_reports_progress_messages() -> None:
    session = FakeSession("<html><body><div>content</div></body></html>")
    messages: list[str] = []
    crawler = Crawler(session=session, progress_callback=messages.append)

    crawler.crawl()

    assert messages[0] == "Crawling page 1: https://quotes.toscrape.com/"
    assert messages[1] == "Completed https://quotes.toscrape.com/. Crawled so far: 1"


def test_normalise_url_keeps_valid_non_trailing_slash_paths() -> None:
    crawler = Crawler()

    assert crawler.normalise_url("/login") == "https://quotes.toscrape.com/login"
    assert crawler.normalise_url("/page/2/") == "https://quotes.toscrape.com/page/2/"


def test_crawler_skips_failed_pages_and_continues() -> None:
    pages = {
        "https://quotes.toscrape.com/": """
        <html>
          <body>
            <a href="/login">Login</a>
            <a href="/page/2/">Page 2</a>
          </body>
        </html>
        """,
        "https://quotes.toscrape.com/login": RuntimeError("temporary failure"),
        "https://quotes.toscrape.com/page/2/": """
        <html>
          <body><div>Second page.</div></body>
        </html>
        """,
    }
    messages: list[str] = []
    crawler = Crawler(session=FakeSession(pages=pages), progress_callback=messages.append)

    crawled_pages = crawler.crawl()

    assert [page["url"] for page in crawled_pages] == [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
    ]
    assert crawler.failed_urls == ["https://quotes.toscrape.com/login"]
    assert any("Failed https://quotes.toscrape.com/login" in message for message in messages)


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
