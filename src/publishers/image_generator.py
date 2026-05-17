import os
import requests
import logging
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

def download_font(font_path="Roboto-Bold.ttf"):
    if not os.path.exists(font_path):
        url = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf"
        logger.info(f"Downloading font from {url}...")
        res = requests.get(url, allow_redirects=True)
        res.raise_for_status()
        with open(font_path, "wb") as f:
            f.write(res.content)
    return font_path

def wrap_text(text, font, max_width, draw):
    lines = []
    words = text.split()
    current_line = []
    
    for word in words:
        current_line.append(word)
        test_line = " ".join(current_line)
        # In Pillow 10+, getlength is preferred, but textbbox works well
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]
        if width > max_width:
            current_line.pop()
            lines.append(" ".join(current_line))
            current_line = [word]
            
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def upload_image(file_path: str) -> str:
    logger.info(f"Uploading {file_path} to uguu.se to get a public URL...")
    url = "https://uguu.se/upload.php"
    with open(file_path, 'rb') as f:
        files = {'files[]': (os.path.basename(file_path), f, 'image/jpeg')}
        res = requests.post(url, files=files, timeout=30)
        res.raise_for_status()
        data = res.json()
        return data['files'][0]['url']

def generate_image(topic: str, date_str: str, image_prompt: str = None) -> tuple[str, str]:
    """
    Generates an image using the dynamic prompt from the Creative Director Agent.
    Adds a YouTube-style text overlay thumbnail using Pillow.
    Uploads to uguu.se to get a public URL.
    Saves the image locally and returns a tuple: (local_file_path, public_image_url).
    """
    logger.info(f"Generating custom image for topic: {topic}")
    
    # We use the prompt from the Creative Director Agent, or fallback to a default
    prompt = image_prompt if image_prompt else f"A highly aesthetic, professional, and engaging photograph representing: {topic}. High quality, trending on social media."
    encoded_prompt = quote(prompt)
    
    # Pollinations generates images via a simple GET request
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true"
    image_filename = f"Daily_Post_Image_{date_str}.jpg"
    
    try:
        # 1. Download raw AI image
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(image_filename, 'wb') as f:
            f.write(response.content)
            
        # 2. Add text overlay using Pillow
        font_path = download_font()
        img = Image.open(image_filename).convert("RGBA")
        
        # Create a transparent overlay for the dark gradient/box
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        font_size = 65
        font = ImageFont.truetype(font_path, font_size)
        
        # Wrap text
        max_text_width = img.width - 100
        wrapped_lines = wrap_text(topic, font, max_text_width, draw)
        
        line_height = font_size + 10
        total_text_height = len(wrapped_lines) * line_height
        
        # Draw a semi-transparent black rectangle at the bottom
        rect_height = total_text_height + 100
        rect_y0 = img.height - rect_height
        draw.rectangle([0, rect_y0, img.width, img.height], fill=(0, 0, 0, 200)) # 200/255 opacity
        
        # Draw the text
        y_text = rect_y0 + 50
        for line in wrapped_lines:
            # Center the text
            bbox = draw.textbbox((0, 0), line, font=font)
            width = bbox[2] - bbox[0]
            x_text = (img.width - width) / 2
            
            draw.text((x_text, y_text), line, font=font, fill=(255, 255, 255, 255))
            y_text += line_height
            
        # Combine the original image with the overlay
        final_img = Image.alpha_composite(img, overlay).convert("RGB")
        final_img.save(image_filename)
        logger.info(f"Text overlay successfully applied.")
        
        # 3. Upload to public host
        public_url = upload_image(image_filename)
        logger.info(f"Image successfully uploaded to {public_url}")
        
        return image_filename, public_url
    except Exception as e:
        logger.error(f"Failed to generate or process image: {e}")
        # Return none or a fallback image if it fails
        return "", ""

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_image("The future of space travel and Mars colonization", "2026_05_15_12_00_00")
