import os
import requests
from .base_publisher import Publisher

class FacebookPublisher(Publisher):
    def publish(self, content: str, image_path: str = None) -> str:
        self.logger.info("Publishing to Facebook Page...")
        
        page_id = os.environ.get("FACEBOOK_PAGE_ID")
        access_token = os.environ.get("FACEBOOK_ACCESS_TOKEN")
        
        if not page_id or not access_token:
            self.logger.error("Missing FACEBOOK_PAGE_ID or FACEBOOK_ACCESS_TOKEN")
            raise ValueError("Facebook credentials are not fully configured.")
            
        url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
        payload = {
            'message': content,
            'access_token': access_token
        }
        
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            data = response.json()
            post_id = data.get('id')
            self.logger.info(f"Successfully published to Facebook! Post ID: {post_id}")
            return f"https://facebook.com/{post_id}"
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to publish to Facebook: {e}")
            if response is not None:
                self.logger.error(f"FB API Response: {response.text}")
            raise
