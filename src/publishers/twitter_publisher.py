import os
import tweepy
from .base_publisher import Publisher

class TwitterPublisher(Publisher):
    def publish(self, content: str, image_path: str = None) -> str:
        self.logger.info("Publishing to Twitter/X...")
        
        consumer_key = os.environ.get("TWITTER_API_KEY")
        consumer_secret = os.environ.get("TWITTER_API_SECRET")
        access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
        access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
        
        if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
            self.logger.error("Missing Twitter API credentials")
            raise ValueError("Twitter credentials are not fully configured.")
            
        client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        # Twitter has a 280 char limit per tweet. 
        # For a simple implementation, we split by double newline or use the whole block if it fits
        # A more complex implementation would parse the "Thread" structure properly
        tweets = content.split("\n\n")
        tweets = [t.strip() for t in tweets if t.strip()]
        
        try:
            previous_tweet_id = None
            for tweet in tweets:
                # Truncate if too long to prevent hard crash
                if len(tweet) > 280:
                    tweet = tweet[:277] + "..."
                    
                if previous_tweet_id is None:
                    response = client.create_tweet(text=tweet)
                    previous_tweet_id = response.data['id']
                    first_tweet_id = previous_tweet_id
                else:
                    response = client.create_tweet(text=tweet, in_reply_to_tweet_id=previous_tweet_id)
                    previous_tweet_id = response.data['id']
                    
            self.logger.info(f"Successfully published thread to Twitter! ID: {first_tweet_id}")
            return f"https://twitter.com/user/status/{first_tweet_id}"
            
        except Exception as e:
            self.logger.error(f"Failed to publish to Twitter: {e}")
            raise
