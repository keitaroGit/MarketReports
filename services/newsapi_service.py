"""
RSS Feed Service for geopolitical news
"""
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

class NewsAPIService:
    RSS_FEEDS = [
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
]

    def get_geopolitical_news(self, limit=10):
        articles = []
        
        for feed in self.RSS_FEEDS:
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
                        articles.append({
                            'title': title,
                            'description': description[:150] if description else '',
                            'url': link,
                            'source': feed['source'],
                            'publishedAt': pub_date
                        })
                        
            except Exception as e:
                print(f"Error fetching RSS from {feed['source']}: {e}")
        
        return articles[:limit]