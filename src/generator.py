import os
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are an expert, world-class social media manager and copywriter.
You will be given a list of today's top trending topics from multiple countries around the world.
Your first task is to evaluate EVERY SINGLE TOPIC from the list. Give each topic a "Global Viral Potential" rating out of 10, and a 1-sentence reason why.
Then, SELECT THE SINGLE BEST TOPIC (the one with the highest rating) to write about.
Once you have selected the top topic, your goal is to write a highly engaging, viral set of posts based on it.

Follow these strict rules:
1. MUST use simple, human-readable English. Do not use overly complex vocabulary. Write like you are speaking to a curious friend.
2. The final content MUST be rated 10/10 for quality. You must explicitly include a section explaining *why* it is a 10/10.
3. The content MUST have a 10/10 "Global Reach" rating (appeals to people worldwide, transcending local boundaries). You must explicitly explain *why* it hits this global reach.
4. The posts must be written in a way that makes people extremely curious, helps them understand the topic easily, and makes them eagerly wait for your next post.
5. You must suggest strategic comments to post on your own content to boost the algorithm and get global reach.
6. CRITICAL: You must include the exact URL of the news source that you selected as the basis for the content.

Format your response exactly as follows, using Markdown:

# 🧠 Global Topic Analysis
(List EVERY topic provided to you. For each, give a rating out of 10 and a brief reason. Example:
- **[Topic Name]**: 4/10 - Too local, won't appeal globally.
- **[Topic Name]**: 10/10 - Universal human interest, highly debateable.)

---

# Selected Topic: [Insert The One Topic With The Highest Rating]

## 📝 1. Website Blog Post
(Write a compelling, easy-to-read blog post. Include an engaging title and a strong hook. End with a cliffhanger or a tease for the next post.)

## 🐦 2. Twitter Thread
(Write a 3-5 tweet thread. Use emojis. Make it punchy. Include a hook in the first tweet. End with a tease for the next post.)

## 📘 3. Facebook Post
(Write an engaging post suitable for Facebook. Ask a question to drive comments.)

## 📸 4. Instagram Caption
(Write an aesthetic, engaging Instagram caption. Include spacing and a good mix of emojis. Provide 10-15 high-reach hashtags.)

## 🔗 5. Source Credits
(Provide the exact source URL of the winning topic here, formatted exactly as "Source: [URL]")

## 💬 6. Strategic Engagement Comments
(Provide 2-3 comments the user should immediately post on their own IG/FB post to spark discussion and game the algorithm for global reach.)

## 🏆 7. Evaluation
**Quality Rating:** 10/10
*Why:* (Explain why this content is a 10/10)

**Global Reach Rating:** 10/10
*Why:* (Explain why this will appeal globally)
"""

def generate_content(topics: list) -> str:
    """
    Calls the Gemini API to select the best topic from a list and generate the posts.
    Returns the generated markdown string.
    """
    logger.info(f"Generating content from {len(topics)} potential global topics...")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable is not set.")
        raise ValueError("GEMINI_API_KEY is required to generate content.")

    genai.configure(api_key=api_key)
    
    # Dynamically find the best available model for your API key
    selected_model_name = 'gemini-1.5-flash'
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                selected_model_name = m.name.replace('models/', '')
                if 'flash' in selected_model_name:
                    break # Prefer flash model if available
        logger.info(f"Auto-selected model: {selected_model_name}")
    except Exception as e:
        logger.warning(f"Could not list models, defaulting to {selected_model_name}: {e}")

    model = genai.GenerativeModel(selected_model_name)
    
    # Format the topics into a bulleted list for the AI
    topics_list_str = "\n".join([f"- {t['topic']} (URL: {t['url']})" for t in topics])
    prompt = f"Here are today's top trending topics from 10 different countries:\n{topics_list_str}\n\nPlease evaluate them, select the absolute best one for global reach, and create the content based on the system instructions."
    
    import time
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(
                contents=[
                    {"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
                    {"role": "user", "parts": [{"text": prompt}]}
                ]
            )
            logger.info("Content successfully generated.")
            return response.text
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                logger.warning(f"Rate limit hit (429). Waiting 60 seconds before retry {attempt + 1}/{max_retries}...")
                time.sleep(60)
            else:
                logger.error(f"Error generating content: {e}")
                raise

if __name__ == "__main__":
    # For local testing, ensure GEMINI_API_KEY is exported in your shell
    logging.basicConfig(level=logging.INFO)
    try:
        result = generate_content([{"topic": "The future of space travel", "url": "http://example.com/space"}, {"topic": "AI Advancements", "url": "http://example.com/ai"}])
        print("\n--- GENERATED CONTENT ---\n")
        print(result)
    except Exception as ex:
        print(f"Failed: {ex}")
