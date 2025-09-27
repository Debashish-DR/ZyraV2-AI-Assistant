import os
import requests
import base64
from dotenv import dotenv_values
import time
import hashlib

env_vars = dotenv_values(".env")

# Check if running on Render
IS_RENDER = os.environ.get('RENDER') is not None

# Enhanced cache to prevent duplicate TTS
tts_cache = {}
last_tts_time = 0
last_tts_text = ""
tts_lock = False
recent_tts_hashes = []

def web_tts_api(text, voice):
    """Web-based TTS using free API services"""
    try:
        # Option 1: Google Translate TTS (free, no API key needed)
        try:
            from gtts import gTTS
            import io
            tts = gTTS(text=text, lang='en', slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            return audio_buffer
        except ImportError:
            pass
        
        # Option 2: Browser-based TTS message
        return None
        
    except Exception as e:
        print(f"Web TTS error: {e}")
        return None

def TextToAudioFile(text, voice):
    if IS_RENDER:
        # On cloud, use web-based TTS or return informative message
        audio_buffer = web_tts_api(text, voice)
        if audio_buffer:
            file_path = f"Data/speech_{hashlib.md5(text.encode()).hexdigest()}.mp3"
            os.makedirs("Data", exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(audio_buffer.getvalue())
            return file_path
        else:
            # Return a placeholder audio file with informative message
            return create_info_audio("Voice features work best on local devices. Web version supports text-based AI chat.")
    
    # Local development with edge-tts
    try:
        import subprocess
        text = str(text).strip()
        if not text:
            return None
        
        cache_key = f"{text.lower()}_{voice}"
        if cache_key in tts_cache and os.path.exists(tts_cache[cache_key]):
            return tts_cache[cache_key]
        
        file_path = f"Data/speech_{hash(cache_key)}.mp3"
        os.makedirs("Data", exist_ok=True)
        
        if os.path.exists(file_path):
            os.remove(file_path)
        
        cmd = [
            'edge-tts',
            '--voice', voice,
            '--text', text.replace('"', '\\"'),
            '--write-media', file_path
        ]
        result = subprocess.run(cmd, check=True, timeout=30, capture_output=True, text=True)
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            tts_cache[cache_key] = file_path
            return file_path
        return None
    except Exception as e:
        print(f"Local TTS error: {e}")
        return None

def create_info_audio(message):
    """Create an informative audio file about cloud limitations"""
    file_path = "Data/cloud_info.mp3"
    if not os.path.exists(file_path):
        # Create a simple text file instead of audio
        with open(file_path, "w") as f:
            f.write(message)
    return file_path

def TextToSpeech(text, voice):
    global last_tts_time, last_tts_text, tts_lock, recent_tts_hashes
    
    if IS_RENDER:
        # On cloud, provide informative response instead of TTS
        info_message = "🔊 **Voice Assistant Notice**\n\n"
        info_message += "🔹 *Text-to-speech works best on local Windows devices*\n"
        info_message += "🔹 *Web version supports all AI chat features via text*\n"
        info_message += "🔹 *Try our desktop app for full voice capabilities*\n\n"
        info_message += "💡 **All AI features work via text input!**"
        return create_info_audio(info_message)
    
    # Original local TTS functionality
    is_muted = os.environ.get('ASSISTANT_MUTED', 'false').lower() == 'true'
    if is_muted:
        print("TTS SKIPPED: Assistant is muted")
        return None
    
    text = str(text).strip()
    if not text:
        return None
    
    current_time = time.time()
    text_hash = hashlib.md5(text.encode()).hexdigest()
    if text_hash in recent_tts_hashes and current_time - last_tts_time < 5:
        print(f"TTS SKIPPED: Recent duplicate '{text[:20]}...'")
        return None
    
    error_phrases = ["sorry", "error", "couldn't", "failed", "unavailable"]
    if any(phrase in text.lower() for phrase in error_phrases) and len(text) < 50:
        print(f"TTS SKIPPED: Error message '{text[:30]}...'")
        return None
    
    if current_time - last_tts_time < 2 and last_tts_text == text:
        print(f"TTS SKIPPED: Same text within 2 seconds '{text[:20]}...'")
        return None
    
    if tts_lock:
        print("TTS SKIPPED: Previous audio still playing")
        return None
    
    print(f"TTS STARTING: '{text[:20]}...'")
    last_tts_time = current_time
    last_tts_text = text
    tts_lock = True
    
    recent_tts_hashes.append(text_hash)
    if len(recent_tts_hashes) > 5:
        recent_tts_hashes.pop(0)
    
    audio_path = TextToAudioFile(text, voice)
    if audio_path and os.path.exists(audio_path):
        tts_lock = False
        return audio_path
    else:
        print("No audio file generated for TTS.")
        tts_lock = False
        return None










# import os
# import subprocess
# from dotenv import dotenv_values
# import time
# import hashlib

# env_vars = dotenv_values(".env")

# # Enhanced cache to prevent duplicate TTS
# tts_cache = {}
# last_tts_time = 0
# last_tts_text = ""
# tts_lock = False
# recent_tts_hashes = []

# def TextToAudioFile(text, voice):
#     text = str(text).strip()
#     if not text:
#         return None
    
#     cache_key = f"{text.lower()}_{voice}"
#     if cache_key in tts_cache and os.path.exists(tts_cache[cache_key]):
#         return tts_cache[cache_key]
    
#     file_path = f"Data/speech_{hash(cache_key)}.mp3"
#     os.makedirs("Data", exist_ok=True)
    
#     if os.path.exists(file_path):
#         os.remove(file_path)
    
#     try:
#         cmd = [
#             'edge-tts',
#             '--voice', voice,
#             '--text', text.replace('"', '\\"'),
#             '--write-media', file_path
#         ]
#         result = subprocess.run(cmd, check=True, timeout=30, capture_output=True, text=True)
#         if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
#             tts_cache[cache_key] = file_path
#             return file_path
#         print("TTS file not generated or empty.")
#         return None
#     except subprocess.CalledProcessError as e:
#         print(f"Edge-TTS error: {e.stderr}")
#         return None
#     except Exception as e:
#         print(f"Edge-TTS error: {str(e)}")
#         return None

# def TextToSpeech(text, voice):
#     global last_tts_time, last_tts_text, tts_lock, recent_tts_hashes
    
#     # FIXED: Check if muted from environment variable or other source
#     is_muted = os.environ.get('ASSISTANT_MUTED', 'false').lower() == 'true'
#     if is_muted:
#         print("TTS SKIPPED: Assistant is muted")
#         return None
    
#     text = str(text).strip()
#     if not text:
#         return None
    
#     current_time = time.time()
    
#     # Skip error messages and duplicates
#     text_hash = hashlib.md5(text.encode()).hexdigest()
#     if text_hash in recent_tts_hashes and current_time - last_tts_time < 5:
#         print(f"TTS SKIPPED: Recent duplicate '{text[:20]}...'")
#         return None
    
#     error_phrases = ["sorry", "error", "couldn't", "failed", "unavailable"]
#     if any(phrase in text.lower() for phrase in error_phrases) and len(text) < 50:
#         print(f"TTS SKIPPED: Error message '{text[:30]}...'")
#         return None
    
#     if current_time - last_tts_time < 2 and last_tts_text == text:
#         print(f"TTS SKIPPED: Same text within 2 seconds '{text[:20]}...'")
#         return None
    
#     if tts_lock:
#         print("TTS SKIPPED: Previous audio still playing")
#         return None
    
#     print(f"TTS STARTING: '{text[:20]}...'")
#     last_tts_time = current_time
#     last_tts_text = text
#     tts_lock = True
    
#     recent_tts_hashes.append(text_hash)
#     if len(recent_tts_hashes) > 5:
#         recent_tts_hashes.pop(0)
    
#     audio_path = TextToAudioFile(text, voice)
#     if audio_path and os.path.exists(audio_path):
#         tts_lock = False
#         return audio_path
#     else:
#         print("No audio file generated for TTS.")
#         tts_lock = False
#         return None

#========================================================================================#

# import pygame
# import random
# import edge_tts
# import os
# import threading
# from dotenv import dotenv_values

# env_vars = dotenv_values(".env")
# AssistantVoice = env_vars.get("AssistantVoice")

# def TextToAudioFile(text):
#     """Synchronous version without async complexity"""
#     file_path = r"Data\speech.mp3"
    
#     if os.path.exists(file_path):
#         os.remove(file_path)
    
#     # Use subprocess to call edge-tts without async
#     import subprocess
#     try:
#         # Escape quotes in text
#         text_escaped = text.replace('"', '\\"')
#         cmd = f'edge-tts --voice "{AssistantVoice}" --text "{text_escaped}" --write-media "{file_path}"'
#         subprocess.run(cmd, shell=True, check=True, timeout=30)
#         return True
#     except Exception as e:
#         print(f"Edge-TTS error: {e}")
#         return False

# def TTS(Text, func=lambda r=None: True):
#     """Synchronous TTS function"""
#     try:
#         # Generate audio file
#         if not TextToAudioFile(Text):
#             return False
            
#         # Initialize pygame mixer
#         pygame.mixer.init()
#         pygame.mixer.music.load(r"Data\speech.mp3")
#         pygame.mixer.music.play()
        
#         # Wait for playback to complete
#         while pygame.mixer.music.get_busy():
#             if func() == False:
#                 break
#             pygame.time.Clock().tick(10)
            
#         return True
        
#     except Exception as e:
#         print(f"Error in TTS: {e}")
#         return False
        
#     finally:
#         try:
#             func(False)
#             if pygame.mixer.get_init():
#                 pygame.mixer.music.stop()
#                 pygame.mixer.quit()
#         except Exception as e:
#             print(f"Error in cleanup: {e}")

# def TextToSpeech(Text, func=lambda r=None: True):
#     """Main text to speech function"""
#     text = str(Text).strip()
#     sentences = [s.strip() for s in text.split('.') if s.strip()]
    
#     if len(sentences) > 4 and len(text) >= 250:
#         short_text = ". ".join(sentences[:2]) + "."
#         responses = ["Should I continue?", "Want me to go on?", "Shall I read more?"]
#         short_text += " " + random.choice(responses)
#         TTS(short_text, func)
#     else:
#         TTS(text, func)

# if __name__ == "__main__":
#     while True:
#         text = input("Enter the text: ")
#         TextToSpeech(text)









