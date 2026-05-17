import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()
import re
import markdown
from trends import get_global_trending_topics
from generator import generate_content_chain
from telegram_sender import send_to_telegram
from publishers.image_generator import generate_image
from publishers.facebook_publisher import FacebookPublisher
from publishers.instagram_publisher import InstagramPublisher
from publishers.twitter_publisher import TwitterPublisher

def extract_section(content: str, header: str) -> str:
    """Extracts everything between [HEADER] and the next [HEADER] or --- or end of string."""
    pattern = rf"{re.escape(header)}\n(.*?)(?=\n\[|\n---\n|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    return match.group(1).strip() if match else ""

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
    
    # 2. Execute the 4-Prompt Agent Chain
    try:
        content, selected_topic, winner_url = generate_content_chain(topics)
    except Exception as e:
        logger.error(f"Pipeline failed at agent chain: {e}")
        # Send an alert to telegram
        try:
            send_to_telegram(f"🚨 **ALERT:** The AI pipeline failed.\n\nError: {e}", "<h1>Pipeline Failed</h1>", datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        except:
            pass
        return
        
    # 4. Parse the content into platform-specific pieces
    logger.info("Parsing content for specific platforms...")
    blog_title = extract_section(content, "[FINAL_BLOG_TITLE]")
    blog_body = extract_section(content, "[FINAL_BLOG_BODY_MARKDOWN WITH REFERENCES]")
    blog_post = f"# {blog_title}\n\n{blog_body}" if blog_title else blog_body
    
    twitter_thread = extract_section(content, "[FINAL_X_THREAD_FOR_MANUAL_POSTING]")
    facebook_post = extract_section(content, "[FINAL_SOCIAL_CAPTION_FACEBOOK WITH IMAGE BINDING & VERIFIED LINK]")
    instagram_caption = extract_section(content, "[FINAL_SOCIAL_CAPTION_INSTAGRAM WITH IMAGE BINDING & BIO TEXT]")
    image_prompt = extract_section(content, "[IMAGE_GENERATOR_THUMBNAIL_PROMPT]")

    # 5. Generate Image for Instagram
    # We pass the AI-generated IMAGE_GENERATOR_THUMBNAIL_PROMPT directly.
    # We still pass selected_topic for the Pillow text overlay.
    logger.info(f"Generating image for AI-selected topic: {selected_topic}")
    date_str = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    image_path, image_url = generate_image(selected_topic, date_str, image_prompt)
    
    # 6. Publish to Social Media (Safely wrapped in try/except so one failure doesn't break others)
    publish_results = []
    
    try:
        if facebook_post:
            fb = FacebookPublisher()
            fb_url = fb.publish(facebook_post, image_url)
            publish_results.append(f"✅ Facebook: {fb_url}")
    except Exception as e:
        publish_results.append(f"❌ Facebook Failed: {e}")
        
    try:
        if instagram_caption and image_url:
            ig = InstagramPublisher()
            ig_url = ig.publish(instagram_caption, image_url)
            publish_results.append(f"✅ Instagram: {ig_url}")
    except Exception as e:
        publish_results.append(f"❌ Instagram Failed: {e}")
        
    # try:
    #     if twitter_thread:
    #         tw = TwitterPublisher()
    #         tw_url = tw.publish(twitter_thread)
    #         publish_results.append(f"✅ Twitter: {tw_url}")
    # except Exception as e:
    #     publish_results.append(f"❌ Twitter Failed: {e}")

    # 7. Save Website HTML to website/ folder
    os.makedirs("website", exist_ok=True)
    website_html_content = markdown.markdown(blog_post)
    website_filename = f"website/post_{date_str}.html"
    
    html_wrapper = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Blog Post - {date_str}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; color: #333; }}
        h1, h2, h3 {{ color: #222; }}
        img {{ max-width: 100%; border-radius: 8px; }}
        a {{ color: #0066cc; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <img src="{image_url}" alt="{selected_topic}">
    {website_html_content}
</body>
</html>"""
    
    with open(website_filename, "w", encoding="utf-8") as f:
        f.write(html_wrapper)
    logger.info(f"Saved Website HTML to {website_filename}")
    publish_results.append(f"✅ Website: Saved locally to {website_filename}")
    
    # 8. Save Full Raw File locally
    local_filename = f"Daily_post_{date_str}.md"
    with open(local_filename, "w", encoding="utf-8") as f:
        f.write(content)

    # 9. Build Telegram delivery files
    # --- Markdown file: full dashboard with status + all content ---
    md_summary = f"# 🚀 Daily Content Report — {date_str}\n\n"
    md_summary += "## 📊 Publishing Status\n\n"
    md_summary += "\n".join(publish_results) + "\n"
    md_summary += f"\n⏳ **Blog Post** — NOT auto-published. Copy from below and post manually.\n"
    md_summary += f"⏳ **X (Twitter) Thread** — NOT auto-published. Copy from below and post manually.\n"
    md_summary += f"\n---\n\n"
    md_summary += f"## 📘 Facebook Post (✅ Auto-Published)\n\n{facebook_post}\n\n---\n\n"
    md_summary += f"## 📸 Instagram Caption (✅ Auto-Published)\n\n{instagram_caption}\n\n---\n\n"
    md_summary += f"## 📝 Blog Post (⏳ Manual — Copy & Paste)\n\n{blog_post}\n\n---\n\n"
    md_summary += f"## 🐦 X (Twitter) Thread (⏳ Manual — Copy & Paste)\n\n{twitter_thread}\n\n---\n\n"
    md_summary += f"## 🖼️ Image Prompt Used\n\n{image_prompt}\n"

    # --- HTML file: styled dashboard ---
    html_blog = markdown.markdown(blog_post)
    html_summary = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Daily Post Report — {date_str}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; color: #333; background: #fafafa; }}
        h1 {{ color: #111; border-bottom: 2px solid #222; padding-bottom: 10px; }}
        h2 {{ color: #222; margin-top: 30px; }}
        .status {{ background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin: 10px 0; }}
        .done {{ border-left: 4px solid #22c55e; }}
        .manual {{ border-left: 4px solid #f59e0b; }}
        img {{ max-width: 100%; border-radius: 8px; margin: 16px 0; }}
        pre {{ background: #f5f5f5; padding: 12px; border-radius: 6px; white-space: pre-wrap; word-wrap: break-word; font-size: 14px; }}
        a {{ color: #0066cc; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        hr {{ border: none; border-top: 1px solid #ddd; margin: 24px 0; }}
    </style>
</head>
<body>
    <h1>🚀 Daily Content Report — {date_str}</h1>
    
    <h2>📊 Publishing Status</h2>
    <div class="status done"><strong>📘 Facebook</strong> — ✅ Auto-Published with Image</div>
    <div class="status done"><strong>📸 Instagram</strong> — ✅ Auto-Published with Image</div>
    <div class="status manual"><strong>📝 Blog Post</strong> — ⏳ Copy from below & post manually</div>
    <div class="status manual"><strong>🐦 X (Twitter)</strong> — ⏳ Copy from below & post manually</div>
    
    <h2>🖼️ Post Image</h2>
    <img src="{image_url}" alt="{selected_topic}">
    
    <hr>
    <h2>📘 Facebook Post (✅ Done)</h2>
    <pre>{facebook_post}</pre>
    
    <hr>
    <h2>📸 Instagram Caption (✅ Done)</h2>
    <pre>{instagram_caption}</pre>
    
    <hr>
    <h2>📝 Blog Post (⏳ Manual)</h2>
    {html_blog}
    
    <hr>
    <h2>🐦 X (Twitter) Thread (⏳ Manual)</h2>
    <pre>{twitter_thread}</pre>
</body>
</html>"""

    try:
        send_to_telegram(md_summary, html_summary, date_str, image_path)
        logger.info("=== Pipeline Completed Successfully ===")
    except Exception as e:
        logger.error(f"Pipeline failed at Telegram delivery: {e}")

if __name__ == "__main__":
    main()
