import logging
from datetime import datetime
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
    
    # 4. Deliver via Telegram
    try:
        send_to_telegram(final_output, date_str)
        logger.info("=== Pipeline Completed Successfully ===")
    except Exception as e:
        logger.error(f"Pipeline failed at Telegram delivery: {e}")
        # Even if delivery fails, we can optionally save locally just in case
        with open(f"failed_delivery_{date_str}.md", "w", encoding="utf-8") as f:
            f.write(final_output)
        logger.info("Saved output locally due to delivery failure.")

if __name__ == "__main__":
    main()
