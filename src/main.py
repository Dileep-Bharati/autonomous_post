import logging
from datetime import datetime
import markdown
from trends import get_global_trending_topics
from generator import generate_content
from telegram_sender import send_to_telegram

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    setup_logging()
    logger = logging.getLogger("main")
    
    logger.info("=== Starting Daily Content Generation Pipeline ===")
    
    # 1. Discover Global Topics
    topics = get_global_trending_topics()
    logger.info(f"Gathered {len(topics)} potential topics from around the world.")
    
    # 2. Generate Content
    try:
        content = generate_content(topics)
    except Exception as e:
        logger.error(f"Pipeline failed at content generation: {e}")
        return
        
    # 3. Format output
    date_str = datetime.now().strftime("%Y_%m_%d")
    
    topics_list_str = "\n".join([f"- {t}" for t in topics])
    
    final_output = f"# 🚀 Daily Viral Content - {date_str}\n\n"
    final_output += f"## 🌍 Global Trending Topics Analysed Today:\n{topics_list_str}\n\n"
    final_output += "---\n\n"
    final_output += content
    
    # Save a local copy of the file for you to view on your computer
    local_filename = f"Daily_post_{date_str}.md"
    with open(local_filename, "w", encoding="utf-8") as f:
        f.write(final_output)
    logger.info(f"Saved local copy to {local_filename}")
    
    # Save an HTML version
    html_content = markdown.markdown(final_output)
    html_filename = f"Daily_post_{date_str}.html"
    
    # Adding basic styling to make the HTML look good
    html_wrapper = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Daily Viral Content - {date_str}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; color: #333; }}
        h1, h2, h3 {{ color: #222; }}
        pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        code {{ font-family: monospace; background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
        blockquote {{ border-left: 4px solid #ddd; padding-left: 10px; margin-left: 0; color: #666; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
    
    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(html_wrapper)
    logger.info(f"Saved HTML copy to {html_filename}")
    
    # 4. Deliver via Telegram
    try:
        send_to_telegram(final_output, html_wrapper, date_str)
        logger.info("=== Pipeline Completed Successfully ===")
    except Exception as e:
        logger.error(f"Pipeline failed at Telegram delivery: {e}")
        # Even if delivery fails, we can optionally save locally just in case
        with open(f"failed_delivery_{date_str}.md", "w", encoding="utf-8") as f:
            f.write(final_output)
        logger.info("Saved output locally due to delivery failure.")

if __name__ == "__main__":
    main()
