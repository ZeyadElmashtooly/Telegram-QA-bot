# Telegram-QA-bot
Telegram AI Bot

A Telegram bot that responds to text and voice messages using Google Gemini AI and Whisper transcription.
The bot can combine voice messages with text captions and respond in text or voice depending on user preference.

Features

Responds to text messages with AI-generated text.

Responds to voice messages with AI-generated voice (TTS).

Combines voice + caption into a single AI prompt.

Users can choose response format (/mode text or /mode voice).

Fully synchronous, easy to run locally.

Uses:

Google Gemini API
 for AI responses

faster-whisper
 for audio transcription

gTTS
 for TTS

Telegram Bot API (python-telegram-bot)

Requirements

Python 3.10+

FFmpeg installed and available in your PATH

Telegram bot token

Google API key for Gemini

Python packages (can be installed via requirements.txt):

python-telegram-bot==20.6
faster-whisper
gTTS
google-generativeai
python-dotenv

Setup

Clone the repository:

git clone https://github.com/<YOUR_USERNAME>/<REPO_NAME>.git
cd <REPO_NAME>


Create a virtual environment and activate it:

python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate


Install dependencies:

pip install -r requirements.txt


Create a .env file in the root directory with your keys:

TELEGRAM_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
FORCE_CUDA=0  # set to 1 if you want to force GPU


Ensure FFmpeg is installed:

ffmpeg -version

Usage

Run the bot:

python bot.py

Commands

/start – Start the bot and see instructions.

/mode text – Set combined voice+caption responses to text.

/mode voice – Set combined voice+caption responses to voice.
