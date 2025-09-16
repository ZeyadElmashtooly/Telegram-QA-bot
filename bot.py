import os
import tempfile
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from ai_worker import handle_text, handle_audio_file
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Store user preferences for combined caption responses
user_modes = {}  # user_id -> "text" or "voice"

# --- Handlers ---
def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update.message.reply_text(
        "Hello 👋 I'm your AI bot!\n"
        "Send me text or voice messages.\n"
        "If you send a voice with a caption, I will combine both.\n"
        "Use /mode text or /mode voice to choose the response format for combined messages."
    )

def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if len(context.args) != 1 or context.args[0].lower() not in ("text", "voice"):
        update.message.reply_text("Usage: /mode text OR /mode voice")
        return

    mode = context.args[0].lower()
    user_modes[user_id] = mode
    update.message.reply_text(f"Response mode for combined messages set to {mode}.")

def ai_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Text-only
    if update.message.text:
        reply_text = handle_text(update.message.text)
        update.message.reply_text(reply_text)
        return

    # Voice-only or voice + caption
    if update.message.voice:
        caption = (update.message.caption or "").strip()
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            file_path = tmp.name
        voice_file = update.message.voice.get_file()
        voice_file.download(file_path)

        reply_text, ogg_path = handle_audio_file(audio_path=file_path, caption_text=caption)

        # Decide mode
        if caption:  # combined prompt → use user preference
            mode = user_modes.get(user_id, "text")
            if mode == "text":
                update.message.reply_text(reply_text)
            else:
                update.message.reply_text(reply_text)
                if ogg_path and os.path.exists(ogg_path):
                    with open(ogg_path, "rb") as f:
                        update.message.reply_voice(voice=InputFile(f, filename="reply.ogg"))
        else:  # voice-only → reply as voice
            update.message.reply_text(reply_text)
            if ogg_path and os.path.exists(ogg_path):
                with open(ogg_path, "rb") as f:
                    update.message.reply_voice(voice=InputFile(f, filename="reply.ogg"))
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mode", set_mode))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_message))
    app.add_handler(MessageHandler(filters.VOICE, ai_message))

    print("🤖 Bot is running...")
    # drop_pending_updates avoids conflict errors from previous runs
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
