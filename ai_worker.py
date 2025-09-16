import os
import subprocess
import tempfile
import logging
from typing import Tuple
from gtts import gTTS
from faster_whisper import WhisperModel
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Logging
logging.basicConfig(filename="ai_worker.log", level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("ai_worker")

# Google Gemini init
API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    logger.warning("GOOGLE_API_KEY not found.")

GENEMODEL_NAME = "gemini-2.5-pro"
gemini_model = genai.GenerativeModel(GENEMODEL_NAME) if API_KEY else None

# Whisper
device = "cuda" if os.getenv("FORCE_CUDA", "0") in ("1","true","yes") else "cpu"
compute_type = "float16" if device=="cuda" else "float32"
whisper_model = WhisperModel("small", device=device, compute_type=compute_type)

# --- Gemini generation ---
def handle_text(msg: str) -> str:
    if not msg:
        return "I didn't receive any text."
    prompt = f"""
    You are a helpful assistant.
    Answer briefly. If you cannot answer, say:
    "I'm sorry, I cannot answer that. Please try asking in another way."
    User: {msg}
    Bot:
    """
    if not gemini_model:
        return "Error: Google API key not configured."
    try:
        response = gemini_model.generate_content(prompt)
        return getattr(response, "text", str(response)).strip()
    except Exception as e:
        logger.exception("Gemini generation failed")
        return f"Error calling Gemini: {e}"

# --- Whisper transcription ---
def transcribe_audio(audio_path: str) -> str:
    try:
        segments, _ = whisper_model.transcribe(audio_path)
        return " ".join([s.text for s in segments]).strip()
    except Exception as e:
        logger.exception("Transcription failed")
        return f"Transcription error: {e}"

# --- TTS & OGG conversion ---
def tts_to_ogg(text: str) -> str:
    try:
        tts = gTTS(text, lang="en")
        with tempfile.TemporaryDirectory() as tmpdir:
            mp3_path = os.path.join(tmpdir, "reply.mp3")
            ogg_path = os.path.join(tmpdir, "reply.ogg")
            tts.save(mp3_path)
            subprocess.run(
                ["ffmpeg", "-y", "-i", mp3_path, "-c:a", "libopus", "-b:a", "64k", ogg_path],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            final_ogg_path = os.path.join(os.getcwd(), "reply.ogg")
            with open(ogg_path, "rb") as src, open(final_ogg_path, "wb") as dst:
                dst.write(src.read())
        return final_ogg_path
    except Exception as e:
        logger.exception("TTS/OGG conversion failed")
        return ""

# --- Combined audio/text handler ---
def handle_audio_file(audio_path: str = None, caption_text="") -> Tuple[str, str]:
    """
    Returns: (reply_text, ogg_path)
    If only text reply is needed, ogg_path can be ignored.
    """
    transcript = ""
    if audio_path:
        if not os.path.exists(audio_path):
            return "Audio file not found.", ""
        transcript = transcribe_audio(audio_path)

    combined_text = (caption_text + " " + transcript).strip() if caption_text else transcript
    if not combined_text:
        return "Could not transcribe audio.", ""

    reply_text = handle_text(combined_text)
    ogg_path = tts_to_ogg(reply_text) if audio_path else ""
    return reply_text, ogg_path
