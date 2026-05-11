"""
RSS Feed Service for geopolitical news
"""
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

class NewsAPIService:
    RSS_FEEDS = [
        {
            'url': 'https://www.investing.com/rss/news.rss',
            'source': 'Investing.com'
        },
        {
            'url': 'https://feeds.bbci.co.uk/news/business/rss.xml',
            'source': 'BBC Business'
        },
        {
            'url': 'https://feeds.bbci.co.uk/news/world/rss.xml',
            'source': 'BBC World'
        },
        {
            'url': 'https://rss.nytimes.com/services/xml/rss/nyt/Business.xml',
            'source': 'NY Times'
        },
        {
            'url': 'https://feeds.marketwatch.com/marketwatch/topstories/',
            'source': 'MarketWatch'
        },
        {
            'url': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
            'source': 'CNBC'
        },
    ]

    def get_geopolitical_news(self, limit=10):
        per_source = []

        for feed in self.RSS_FEEDS:
            source_articles = []
            try:
                response = requests.get(feed['url'], timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0'
                })
                if response.status_code != 200:
                    continue

                root = ET.fromstring(response.content)
                channel = root.find('channel')
                if channel is None:
                    continue

                items = channel.findall('item')
                for item in items[:5]:
                    title = item.findtext('title', '')
                    description = item.findtext('description', '')
                    link = item.findtext('link', '')
                    pub_date = item.findtext('pubDate', '')

                    if title:
                        source_articles.append({
                            'title': title,
                            'description': description[:150] if description else '',
                            'url': link,
                            'source': feed['source'],
                            'publishedAt': pub_date
                        })

            except Exception as e:
                print(f"Error fetching RSS from {feed['source']}: {e}")

            if source_articles:
                per_source.append({
                    'source': feed['source'],
                    'articles': source_articles,
                })

        # Investing.comを優先：3件、他は2件
        result = []
        for src in per_source:
            count = 3 if src['source'] == 'Investing.com' else 2
            result.extend(src['articles'][:count])

        return result[:limit]