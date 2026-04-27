import os
import io
import logging
import requests

logger = logging.getLogger(__name__)

def send_to_telegram(content: str, date_str: str):
    """
    Sends the generated content to a Telegram chat as a markdown document.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logger.error("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID environment variables are not set.")
        raise ValueError("Telegram credentials are required to send the message.")

    logger.info("Sending content to Telegram...")
    
    # We send it as a document so we don't hit the 4096 character limit of regular messages
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    
    # Create an in-memory file
    file_name = f"Daily_Post_{date_str}.md"
    file_bytes = io.BytesIO(content.encode('utf-8'))
    
    files = {
        'document': (file_name, file_bytes, 'text/markdown')
    }
    
    data = {
        'chat_id': chat_id,
        'caption': f"🚀 Here is your highly-rated, automated content for {date_str}!"
    }
    
    try:
        response = requests.post(url, data=data, files=files)
        response.raise_for_status()
        logger.info("Successfully sent document to Telegram.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send to Telegram: {e}")
        if response is not None:
            logger.error(f"Telegram API Response: {response.text}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        send_to_telegram("# Test\nThis is a test document from Antigravity.", "2026_04_27")
    except Exception as ex:
        print(f"Failed: {ex}")
