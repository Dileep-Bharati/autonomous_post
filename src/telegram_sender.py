import os
import io
import logging
import requests

logger = logging.getLogger(__name__)

def send_to_telegram(md_content: str, html_content: str, date_str: str):
    """
    Sends the generated content to a Telegram chat as a markdown and html document.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logger.error("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID environment variables are not set.")
        raise ValueError("Telegram credentials are required to send the message.")

    logger.info("Sending content to Telegram...")
    
    # We send it as a document so we don't hit the 4096 character limit of regular messages
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    
    # 1. Send Markdown File
    md_file_name = f"Daily_Post_{date_str}.md"
    md_file_bytes = io.BytesIO(md_content.encode('utf-8'))
    
    md_files = {
        'document': (md_file_name, md_file_bytes, 'text/markdown')
    }
    
    md_data = {
        'chat_id': chat_id,
        'caption': f"🚀 Here is your Markdown content for {date_str}!"
    }
    
    response = None
    try:
        response = requests.post(url, data=md_data, files=md_files)
        response.raise_for_status()
        logger.info("Successfully sent Markdown document to Telegram.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Markdown to Telegram: {e}")
        if response is not None:
            logger.error(f"Telegram API Response: {response.text}")
        raise

    # 2. Send HTML File
    html_file_name = f"Daily_Post_{date_str}.html"
    html_file_bytes = io.BytesIO(html_content.encode('utf-8'))
    
    html_files = {
        'document': (html_file_name, html_file_bytes, 'text/html')
    }
    
    html_data = {
        'chat_id': chat_id,
        'caption': f"🌐 Here is your HTML formatted content for {date_str}!"
    }
    
    response = None
    try:
        response = requests.post(url, data=html_data, files=html_files)
        response.raise_for_status()
        logger.info("Successfully sent HTML document to Telegram.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send HTML to Telegram: {e}")
        if response is not None:
            logger.error(f"Telegram API Response: {response.text}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        send_to_telegram("# Test\nThis is a test document from Antigravity.", "<h1>Test</h1><p>This is a test document from Antigravity.</p>", "2026_04_27")
    except Exception as ex:
        print(f"Failed: {ex}")
