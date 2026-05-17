import os
import logging
import time
import re
import google.generativeai as genai

logger = logging.getLogger(__name__)

PROMPT_1 = """
You are the "Executive Editor" inside an automated newsroom system. Analyze the 20 incoming international trending topics scraped from Google Trends.

CRITICAL FILTERING RULES:
- IGNORE: Localized politics or dry, technical news. 
- IGNORE: Sensitive medical/health crises (like virus outbreaks or pandemics) that trigger platform shadowbans or auto-deletions.
- PRIORITIZE: Universal human interest, highly debatable cultural topics, or massive tech/AI breakthroughs that bridge international audiences.

SCORING TASK:
1. Rate each of the 20 raw topics out of 10 based on "Global Viral Potential."
2. Select the single highest-rated topic as the winner. Mark it as "10/10 WINNER".
3. Maintain and isolate the original source URL attached to that winner.

OUTPUT STRUCTURE:
[Topic 1] - [Score]/10
...
WINNER_TOPIC: [Title of Winning Topic]
WINNER_URL: [Source URL from trends.py]
"""

PROMPT_2 = """
You are a world-class Viral Content Creator and Creative Director. Take the provided WINNER_TOPIC and write a full content text suite containing a Website Blog Post, a Facebook Post, an Instagram Caption, and an X (Twitter) Thread.

WRITING MANDATES:
1. THE HOOK: Start with a sharp, counter-intuitive statement or result-first hook in the very first line. No slow introductions.
2. STRUCTURE: Apply the PAS (Problem-Agitation-Solution) framework for social media posts, and the AIDA framework for the blog post.
3. VISUAL FORMATTING: Enforce extreme mobile skimmability. You must use one-sentence paragraphs, generous white space, and bold key phrases.
4. TONE: Conversational, authoritative, and native to natural human speech.

CREATIVE DIRECTION MANDATES (IMAGE OVERLAY):
1. IMAGE PROMPT GENERATION: Generate a highly descriptive, cinematic, high-contrast prompt optimized for an AI Image Generator to build a background image representing the winning topic.
2. IMAGE EDITING BLUEPRINT: Create a step-by-step text instruction set for the automated image editor to overlay the 10/10 winning topic title cleanly onto the lower half of the generated image (using a semi-transparent dark header bar and bold white overlay text).

WINNER_TOPIC: {winner_topic}

OUTPUT STRUCTURE:
---
[RAW_BLOG_DRAFT]
---
[RAW_FACEBOOK_DRAFT]
---
[RAW_INSTAGRAM_DRAFT]
---
[RAW_X_THREAD_DRAFT]
---
[RAW_IMAGE_PROMPT]
---
[IMAGE_EDITING_BLUEPRINT]
---
"""

PROMPT_3 = """
You are a strict Corporate Attorney. Audit and rewrite the provided text drafts and creative direction instructions against legal liabilities and platform signatures.

REWRITE MANDATES:
1. THE DE-AI CLEANSE: Delete and replace all robotic AI clichés: "delve", "tapestry", "in conclusion", "furthermore", "revolutionary", "pivotal", "vital", "masterclass". Replace them with punchy human verbs.
2. DEFAMATION & SAFETY: Ensure all critiques are framed around objective, fact-based phrases. Strip out subjective defamatory terms like "scam" or "fraud".
3. PLATFORM LIMITS: Keep Facebook and Instagram captions under 2,200 characters. For X (Twitter), ensure no single tweet draft exceeds 280 characters. Format the blog in clean Markdown hierarchy (## and ###).

RAW TEXT TO AUDIT:
{raw_text}
"""

PROMPT_4 = """
You are "Agent 4 (The Fact, Link & Asset Validator)." Your final job is to inject the verified source reference URL into the content suite, bundle the finalized text strings with your image execution commands, and output the structure destined for your Telegram .md and .html files.

LINK & IMAGE BUNDLING MANDATES:
1. For the Website Blog Post: Add a concluding section called "### 🌐 References & Fact-Checking" and insert the WINNER_URL as a markdown link.
2. For the Facebook Post: Ensure this post is explicitly marked to include the newly generated and edited image. End the post natively with: "👉 Read the full verified source and fact-check here: [WINNER_URL]"
3. For the Instagram Caption: Ensure this caption is paired with the newly generated image. Append this line before your hashtags: "🔗 Verified source link available in our bio! Fact-check the full story."
4. For the X (Twitter) Thread: Structure the text into numbered blocks (e.g., [1/3], [2/3]) so it can be easily copied and manually posted. The final tweet in the thread must read: "🔗 Read the full verified story and fact-check here: [WINNER_URL]"

TECHNICAL OUTPUT ONLY:
Do not include any conversational meta-commentary, friendly introductions, or summaries. Output ONLY the raw production-ready payload strings.

WINNER_URL TO USE: {winner_url}
AUDITED CONTENT: 
{audited_content}

FINAL PAYLOAD OUTPUT STRUCTURING:
---
[IMAGE_GENERATOR_THUMBNAIL_PROMPT]
...
---
[IMAGE_EDITING_BLUEPRINT_FOR_INSTA_AND_FB]
...
---
[FINAL_BLOG_TITLE]
...
[FINAL_BLOG_BODY_MARKDOWN WITH REFERENCES]
---
[FINAL_SOCIAL_CAPTION_FACEBOOK WITH IMAGE BINDING & VERIFIED LINK]
...
---
[FINAL_SOCIAL_CAPTION_INSTAGRAM WITH IMAGE BINDING & BIO TEXT]
...
---
[FINAL_X_THREAD_FOR_MANUAL_POSTING]
...
---
"""

def _call_gemini(model, prompt_text: str, role_system_prompt: str = None) -> str:
    max_retries = 3
    
    contents = []
    if role_system_prompt:
        contents.append({"role": "user", "parts": [{"text": role_system_prompt}]})
    contents.append({"role": "user", "parts": [{"text": prompt_text}]})
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(contents=contents)
            return response.text
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                logger.warning(f"Rate limit hit (429). Waiting 60 seconds before retry {attempt + 1}/{max_retries}...")
                time.sleep(60)
            else:
                logger.error(f"Error generating content: {e}")
                raise
    return ""

def generate_content_chain(topics: list) -> tuple[str, str, str]:
    """
    Executes the 4-step AI agent chain.
    Returns: (final_payload_markdown, winner_topic, winner_url)
    """
    logger.info("Initializing 4-Prompt Multi-Agent Chain...")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required.")

    genai.configure(api_key=api_key)
    # Using gemini-2.5-flash as requested
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # === AGENT 1: Executive Editor ===
    logger.info("Agent 1 (Executive Editor) is filtering topics...")
    topics_list_str = "\n".join([f"- {t['topic']} (URL: {t['url']})" for t in topics])
    res1 = _call_gemini(model, f"Here are the 20 raw topics:\n{topics_list_str}", PROMPT_1)
    
    winner_topic = ""
    winner_url = ""
    match_topic = re.search(r"WINNER_TOPIC:\s*(.+)", res1, re.IGNORECASE)
    if match_topic:
        winner_topic = match_topic.group(1).strip()
    match_url = re.search(r"WINNER_URL:\s*(.+)", res1, re.IGNORECASE)
    if match_url:
        winner_url = match_url.group(1).strip()
        
    if not winner_topic:
        logger.warning("Failed to extract WINNER_TOPIC. Falling back to top topic.")
        winner_topic = topics[0]['topic']
        winner_url = topics[0]['url']
        
    logger.info(f"Agent 1 selected: {winner_topic}")
    
    # === AGENT 2: Creative Director ===
    logger.info("Agent 2 (Creative Director) is writing raw drafts...")
    prompt2_filled = PROMPT_2.replace("{winner_topic}", winner_topic)
    res2 = _call_gemini(model, prompt2_filled)
    
    # === AGENT 3: Corporate Attorney ===
    logger.info("Agent 3 (Corporate Attorney) is auditing drafts for safety & cliches...")
    prompt3_filled = PROMPT_3.replace("{raw_text}", res2)
    res3 = _call_gemini(model, prompt3_filled)
    
    # === AGENT 4: Asset Validator ===
    logger.info("Agent 4 (Asset Validator) is formatting final payload...")
    prompt4_filled = PROMPT_4.replace("{winner_url}", winner_url).replace("{audited_content}", res3)
    res4 = _call_gemini(model, prompt4_filled)
    
    logger.info("4-Prompt Chain successfully completed.")
    return res4, winner_topic, winner_url

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        payload, t, u = generate_content_chain([{"topic": "The future of space travel", "url": "http://example.com/space"}])
        print("\n--- FINAL PAYLOAD ---\n")
        print(payload)
    except Exception as ex:
        print(f"Failed: {ex}")
