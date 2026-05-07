from src.crawler import Crawler, CrawlerConfig


def test_crawler_uses_default_config() -> None:
    crawler = Crawler()
    assert crawler.config.base_url == "https://quotes.toscrape.com/"
    assert crawler.config.politeness_delay == 6


def test_crawler_accepts_custom_config() -> None:
    config = CrawlerConfig(base_url="https://example.com", politeness_delay=10)
    crawler = Crawler(config)
    assert crawler.config == config

