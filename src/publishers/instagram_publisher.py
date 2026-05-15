import os
import time
import requests
from .base_publisher import Publisher

class InstagramPublisher(Publisher):
    def publish(self, content: str, image_url: str = None) -> str:
        self.logger.info("Publishing to Instagram...")
        
        ig_user_id = os.environ.get("INSTAGRAM_USER_ID")
        access_token = os.environ.get("FACEBOOK_ACCESS_TOKEN") # Uses same token as FB
        
        if not ig_user_id or not access_token or not image_url:
            self.logger.error("Missing INSTAGRAM_USER_ID, FACEBOOK_ACCESS_TOKEN, or image_url")
            raise ValueError("Instagram credentials/image not fully configured.")
            
        # Step 1: Create the media container
        container_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
        container_payload = {
            'image_url': image_url,
            'caption': content,
            'access_token': access_token
        }
        
        try:
            res = requests.post(container_url, data=container_payload)
            res.raise_for_status()
            creation_id = res.json().get('id')
            self.logger.info(f"Created IG media container: {creation_id}. Waiting for processing...")
            
            # Wait a few seconds for IG to process the image from the URL
            time.sleep(5)
            
            # Step 2: Publish the container
            publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
            publish_payload = {
                'creation_id': creation_id,
                'access_token': access_token
            }
            
            pub_res = requests.post(publish_url, data=publish_payload)
            pub_res.raise_for_status()
            post_id = pub_res.json().get('id')
            
            self.logger.info(f"Successfully published to Instagram! Post ID: {post_id}")
            return f"https://instagram.com/p/{post_id}" # Note: actual permalink requires another API call, this is just ID
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to publish to Instagram: {e}")
            raise
