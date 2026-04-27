# Autonomous Content Generator

This project is an automated pipeline that:
1. Finds today's top trending topic using Google Trends.
2. Uses Google Gemini AI to write highly-engaging, 10/10 quality posts tailored for your Blog, Twitter, Facebook, and Instagram.
3. Automatically delivers the fully formatted content directly to your Telegram app.

## Project Structure

```text
├── src/
│   ├── trends.py           # Fetches trending topics
│   ├── generator.py        # Generates content via Gemini API
│   ├── telegram_sender.py  # Sends content to Telegram
│   └── main.py             # Orchestrates the entire flow
├── .github/
│   └── workflows/
│       └── daily_post.yml  # GitHub Actions workflow for automation
├── requirements.txt        # Python dependencies
└── README.md               # You are here
```

## How to Test Locally

If you want to run this on your local machine to test it:

1. **Install Dependencies:**
   Open a terminal in this folder and run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your Environment Variables:**
   You must set your API keys in your terminal before running the script.
   ```bash
   export GEMINI_API_KEY="your_gemini_key_here"
   export TELEGRAM_BOT_TOKEN="your_bot_token_here"
   export TELEGRAM_CHAT_ID="your_chat_id_here"
   ```

3. **Run the Script:**
   ```bash
   cd src
   python main.py
   ```
   *Check your Telegram! A beautiful markdown document should arrive in seconds.*

## How to Deploy to GitHub (Free Automation)

1. Create a new empty repository on your GitHub account.
2. Push all these files to that repository.
3. Go to your GitHub Repository -> **Settings** -> **Secrets and variables** -> **Actions**.
4. Add three new **Repository Secrets**:
   - Name: `GEMINI_API_KEY` | Secret: (Your Key)
   - Name: `TELEGRAM_BOT_TOKEN` | Secret: (Your Token)
   - Name: `TELEGRAM_CHAT_ID` | Secret: (Your ID)
5. Go to the **Actions** tab in your repository.
6. Select **Daily Content Generator** and click **Run workflow**.

That's it! It will now automatically run every day at 08:00 UTC and send the latest trending post directly to your phone.
