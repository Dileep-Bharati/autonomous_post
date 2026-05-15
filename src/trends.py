import logging
import requests
import xml.etree.ElementTree as ET
import time

logger = logging.getLogger(__name__)

def get_global_trending_topics():
    """
    Fetches the top news/trending topics from 10 major countries using Google News RSS.
    This completely bypasses the Google Trends 404 block.
    Returns a list of dictionaries with 'topic' and 'url' keys.
    """
    # Google News RSS parameters for 10 countries
    countries_rss = {
        'United States': 'hl=en-US&gl=US&ceid=US:en',
        'India': 'hl=en-IN&gl=IN&ceid=IN:en',
        'United Kingdom': 'hl=en-GB&gl=GB&ceid=GB:en',
        'France': 'hl=fr&gl=FR&ceid=FR:fr',
        'Russia': 'hl=ru&gl=RU&ceid=RU:ru',
        'Japan': 'hl=ja&gl=JP&ceid=JP:ja',
        'Germany': 'hl=de&gl=DE&ceid=DE:de',
        'Brazil': 'hl=pt-BR&gl=BR&ceid=BR:pt-419',
        'Canada': 'hl=en-CA&gl=CA&ceid=CA:en',
        'Australia': 'hl=en-AU&gl=AU&ceid=AU:en'
    }
    
    global_topics = set()
    logger.info("Fetching real-time trending news from 10 major countries via RSS...")

    for country, params in countries_rss.items():
        try:
            logger.info(f"Checking {country}...")
            url = f"https://news.google.com/rss?{params}"
            
            # Use a standard browser user-agent to prevent blocks
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            items = root.findall('.//item')
            
            # Grab top 2 stories
            if len(items) >= 2:
                # Remove the "- Source Name" at the end of Google News titles for cleaner topics
                top_1_title = items[0].find('title').text.rsplit(' - ', 1)[0]
                top_1_link = items[0].find('link').text
                top_2_title = items[1].find('title').text.rsplit(' - ', 1)[0]
                top_2_link = items[1].find('link').text
                
                # Using a tuple to add to set to avoid duplicates
                global_topics.add((top_1_title, top_1_link))
                global_topics.add((top_2_title, top_2_link))
                
            time.sleep(1) # Be polite to the server
            
        except Exception as e:
            logger.warning(f"Could not fetch trends for {country}. Skipping. Error: {e}")
            
    # If we successfully got topics, return them as a list of dicts
    if global_topics:
        logger.info(f"Successfully gathered {len(global_topics)} unique real-time topics from around the world.")
        return [{"topic": t[0], "url": t[1]} for t in global_topics]
    else:
        logger.warning("Could not fetch any topics globally. Using fallback topics.")
        return [
            {"topic": "Artificial Intelligence breakthroughs", "url": "https://news.google.com"},
            {"topic": "Climate Change Solutions", "url": "https://news.google.com"},
            {"topic": "Space Exploration", "url": "https://news.google.com"}
        ]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    topics = get_global_trending_topics()
    print(f"Global Topics:\n{topics}")
