import os
import requests
import logging
from urllib.parse import quote

logger = logging.getLogger(__name__)

def generate_image(topic: str, date_str: str) -> str:
    """
    Generates an image for the given topic using the free Pollinations.ai API.
    Saves the image locally and returns a tuple: (local_file_path, public_image_url).
    """
    logger.info(f"Generating custom image for topic: {topic}")
    
    # We create a highly descriptive prompt for the AI
    prompt = f"A highly aesthetic, professional, and engaging photograph representing: {topic}. High quality, trending on social media."
    encoded_prompt = quote(prompt)
    
    # Pollinations generates images via a simple GET request
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true"
    
    image_filename = f"Daily_Post_Image_{date_str}.jpg"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(image_filename, 'wb') as f:
            f.write(response.content)
            
        logger.info(f"Image successfully generated and saved to {image_filename}")
        return image_filename, url
    except Exception as e:
        logger.error(f"Failed to generate image: {e}")
        # Return none or a fallback image if it fails
        return "", ""

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_image("The future of space travel", "2026_05_15_12_00_00")
