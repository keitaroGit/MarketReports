"""
NewsAPI Service for geopolitical news
"""
import os
import requests
from datetime import datetime, timedelta

class NewsAPIService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('NEWSAPI_KEY')
        self.base_url = 'https://newsapi.org/v2/everything'
    
    def get_geopolitical_news(self, limit=10):
        """
        Fetch geopolitical risk-related news
        
        Returns:
            List of news articles
        """
        # Keywords for geopolitical risks
        keywords = [
            'geopolitical risk',
            'trade war',
            'sanctions',
            'international tensions',
            'market volatility'
        ]
        
        query = ' OR '.join(keywords)
        
        # Get news from the last 7 days
        from_date = (datetime.now() - timedelta(days=7)).isoformat()
        
        try:
            params = {
                'q': query,
                'from': from_date,
                'sortBy': 'relevancy',
                'language': 'en',
                'apiKey': self.api_key,
                'pageSize': limit
            }
            
            response = requests.get(self.base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                for article in data.get('articles', [])[:limit]:
                    articles.append({
                        'title': article.get('title'),
                        'description': article.get('description'),
                        'url': article.get('url'),
                        'source': article.get('source', {}).get('name'),
                        'publishedAt': article.get('publishedAt'),
                        'image': article.get('urlToImage')
                    })
                
                return articles
            else:
                return []
        except Exception as e:
            print(f"Error fetching news: {str(e)}")
            return []
    
    def search_news(self, query, limit=10):
        """
        Search for specific news
        
        Args:
            query: Search query string
            limit: Number of results
        
        Returns:
            List of news articles
        """
        try:
            from_date = (datetime.now() - timedelta(days=30)).isoformat()
            
            params = {
                'q': query,
                'from': from_date,
                'sortBy': 'relevancy',
                'language': 'en',
                'apiKey': self.api_key,
                'pageSize': limit
            }
            
            response = requests.get(self.base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                for article in data.get('articles', [])[:limit]:
                    articles.append({
                        'title': article.get('title'),
                        'description': article.get('description'),
                        'url': article.get('url'),
                        'source': article.get('source', {}).get('name'),
                        'publishedAt': article.get('publishedAt'),
                        'image': article.get('urlToImage')
                    })
                
                return articles
            else:
                return []
        except Exception as e:
            print(f"Error searching news: {str(e)}")
            return []
