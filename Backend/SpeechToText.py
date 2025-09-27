import os
from dotenv import dotenv_values
import tempfile
import time

env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en")

# Check if running on Render
IS_RENDER = os.environ.get('RENDER') is not None

def QueryModifier(query):
    """Improve query formatting"""
    if not query or "sorry" in query.lower() or "didn't catch" in query.lower():
        return "Sorry, I didn't catch that. Could you repeat?"
    
    new_query = query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "what's", "when", "where", "which", "who", "whom", "whose", "why", "is", "are", "can", "could", "would", "should", "do", "does", "did"]
    
    if any(word + " " in new_query for word in question_words):
        if query_words and query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words and query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    return new_query.capitalize()

def SpeechRecognition(audio_path):
    """Cloud-compatible speech recognition"""
    if IS_RENDER:
        return "🎤 **Voice Assistant Notice**\n\n" + \
               "🔹 *Speech-to-text works best on local Windows devices* \n" + \
               "🔹 *Web version supports all AI chat features via text* \n" + \
               "🔹 *Try our desktop app for full voice capabilities* \n\n" + \
               "💡 **Tip:** You can still use all AI features by typing your messages!"
    
    try:
        # Try to import required modules
        try:
            import speech_recognition as sr
            from pydub import AudioSegment
        except ImportError as e:
            return f"🔧 Voice features require: pip install speechrecognition pydub. Use text input for now."
        
        # Check if audio file exists
        if not os.path.exists(audio_path):
            return "Audio file not found. Please try recording again."
        
        # Validate audio file size
        file_size = os.path.getsize(audio_path)
        if file_size == 0:
            return "Audio file is empty. Please try recording again."
        if file_size > 10 * 1024 * 1024:
            return "Audio file too large. Please try a shorter recording."
        
        temp_filename = None
        try:
            # Convert audio to compatible format
            audio = AudioSegment.from_file(audio_path)
            
            # Check audio duration
            duration = len(audio) / 1000.0
            if duration < 0.5:
                return "Recording too short. Please speak for at least 1 second."
            if duration > 60:
                return "Recording too long. Please keep under 60 seconds."
            
            # Process audio
            audio = audio.set_frame_rate(16000)
            audio = audio.set_channels(1)
            audio = audio.normalize()
            
            # Create temporary file
            temp_filename = f"/tmp/temp_audio_{int(time.time() * 1000)}.wav"
            audio.export(temp_filename, format="wav")
            
            # Initialize recognizer
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 300
            recognizer.dynamic_energy_threshold = True
            recognizer.pause_threshold = 0.8
            
            # Recognize speech
            with sr.AudioFile(temp_filename) as source:
                recognizer.adjust_for_ambient_noise(source, duration=1.0)
                audio_data = recognizer.record(source)
                
            # Use Google Speech Recognition
            text = recognizer.recognize_google(audio_data, language=InputLanguage)
            text = QueryModifier(text)
            
            return text
            
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand the audio. Please try speaking more clearly."
            
        except sr.RequestError as e:
            return f"Speech service unavailable. Please check your internet connection."
            
        except Exception as e:
            return f"Error processing audio. Please try again."
            
        finally:
            # Clean up temporary files
            if temp_filename and os.path.exists(temp_filename):
                try:
                    os.remove(temp_filename)
                except:
                    pass
                
    except Exception as e:
        return f"Unexpected error in speech recognition. Please use text input."

def process_audio(audio_path):
    """Main function to process audio with cloud detection"""
    if IS_RENDER:
        return "🎤 **Web Version Notice**\n\n" + \
               "✅ *Working Features:* AI Chat, Web Search, Image Generation\n" + \
               "🔒 *Local-Only Features:* Voice Control\n" + \
               "💡 *Tip:* Type your messages to use all AI features!"
    
    # Try full speech recognition for local development
    try:
        import speech_recognition as sr
        from pydub import AudioSegment
        return SpeechRecognition(audio_path)
    except ImportError:
        return "🔧 **Setup Required:**\n\nTo enable voice features locally:\n1. Install: pip install speechrecognition pydub\n2. Web version supports text-based AI chat"








# import os
# from dotenv import dotenv_values
# import tempfile
# import time

# env_vars = dotenv_values(".env")
# InputLanguage = env_vars.get("InputLanguage", "en")

# def QueryModifier(query):
#     """Improve query formatting"""
#     if not query or "sorry" in query.lower() or "didn't catch" in query.lower():
#         return "Sorry, I didn't catch that. Could you repeat?"
    
#     new_query = query.lower().strip()
#     query_words = new_query.split()
#     question_words = ["how", "what", "what's", "when", "where", "which", "who", "whom", "whose", "why", "is", "are", "can", "could", "would", "should", "do", "does", "did"]
    
#     if any(word + " " in new_query for word in question_words):
#         if query_words and query_words[-1][-1] in ['.', '?', '!']:
#             new_query = new_query[:-1] + "?"
#         else:
#             new_query += "?"
#     else:
#         if query_words and query_words[-1][-1] in ['.', '?', '!']:
#             new_query = new_query[:-1] + "."
#         else:
#             new_query += "."
#     return new_query.capitalize()

# def SpeechRecognition(audio_path):
#     """Cloud-compatible speech recognition with proper error handling"""
#     try:
#         # Check if running on cloud server
#         if os.environ.get('RENDER'):
#             return "🎤 Speech-to-text works best on local devices. Please use text input or try our mobile app for voice features! 📱"
        
#         # Try to import required modules
#         try:
#             import speech_recognition as sr
#             from pydub import AudioSegment
#         except ImportError as e:
#             return f"🔧 Voice features require additional setup: {str(e)}. Please use text input for now."
        
#         # Check if audio file exists
#         if not os.path.exists(audio_path):
#             return "Audio file not found. Please try recording again."
        
#         # Validate audio file size
#         file_size = os.path.getsize(audio_path)
#         if file_size == 0:
#             return "Audio file is empty. Please try recording again."
#         if file_size > 10 * 1024 * 1024:  # 10MB limit
#             return "Audio file too large. Please try a shorter recording."
        
#         temp_filename = None
#         try:
#             # Convert audio to compatible format
#             audio = AudioSegment.from_file(audio_path)
            
#             # Check audio duration
#             duration = len(audio) / 1000.0  # Convert ms to seconds
#             if duration < 0.5:
#                 return "Recording too short. Please speak for at least 1 second."
#             if duration > 60:
#                 return "Recording too long. Please keep under 60 seconds."
            
#             # Process audio for better recognition
#             audio = audio.set_frame_rate(16000)  # Standard for speech recognition
#             audio = audio.set_channels(1)        # Mono audio
#             audio = audio.normalize()            # Normalize volume
            
#             # Create temporary file
#             temp_filename = f"/tmp/temp_audio_{int(time.time() * 1000)}.wav"
#             audio.export(temp_filename, format="wav")
            
#             # Initialize recognizer
#             recognizer = sr.Recognizer()
#             recognizer.energy_threshold = 300
#             recognizer.dynamic_energy_threshold = True
#             recognizer.pause_threshold = 0.8
            
#             # Recognize speech
#             with sr.AudioFile(temp_filename) as source:
#                 recognizer.adjust_for_ambient_noise(source, duration=1.0)
#                 audio_data = recognizer.record(source)
                
#             # Use Google Speech Recognition
#             text = recognizer.recognize_google(audio_data, language=InputLanguage)
#             text = QueryModifier(text)
            
#             return text
            
#         except sr.UnknownValueError:
#             return "Sorry, I couldn't understand the audio. Please try speaking more clearly."
            
#         except sr.RequestError as e:
#             return f"Speech service unavailable. Please check your internet connection. Error: {str(e)}"
            
#         except Exception as e:
#             return f"Error processing audio: {str(e)}. Please try again."
            
#         finally:
#             # Clean up temporary files
#             if temp_filename and os.path.exists(temp_filename):
#                 try:
#                     os.remove(temp_filename)
#                 except:
#                     pass
                
#     except Exception as e:
#         return f"Unexpected error in speech recognition: {str(e)}. Please use text input."

# # Alternative cloud-based speech recognition (for future implementation)
# def CloudSpeechRecognition(audio_file):
#     """Future implementation for cloud-based speech recognition"""
#     try:
#         # This would integrate with cloud speech APIs like:
#         # - Google Cloud Speech-to-Text
#         # - AWS Transcribe
#         # - Azure Speech Services
        
#         # For now, return a message about cloud limitations
#         return "🔒 Cloud speech recognition requires additional API setup. Voice features work best on local devices. 📱"
        
#     except Exception as e:
#         return f"Cloud speech recognition error: {str(e)}"

# # Fallback function for when dependencies are missing
# def SimpleSpeechRecognition(audio_path):
#     """Simple fallback when speech recognition is not available"""
#     return "🎤 Voice features require speech recognition setup. Please use text input or set up your local environment for full functionality. 🔧"

# # Main function that handles all cases
# def process_audio(audio_path):
#     """
#     Main function to process audio with proper fallbacks
#     Returns recognized text or error message
#     """
#     # Check if this is a cloud environment
#     if os.environ.get('RENDER') or os.environ.get('PYTHONANYWHERE'):
#         return "🎤 **Voice Assistant Notice:** \n\n" + \
#                "🔹 *Speech-to-text works best on local Windows devices* \n" + \
#                "🔹 *Web version supports all AI chat features via text* \n" + \
#                "🔹 *Try our desktop app for full voice capabilities* \n" + \
#                "🔹 *Mobile app coming soon with voice support* \n\n" + \
#                "💡 **Tip:** You can still use all AI features by typing your messages!"
    
#     # Try full speech recognition
#     try:
#         import speech_recognition as sr
#         from pydub import AudioSegment
#         # If imports work, use full functionality
#         return SpeechRecognition(audio_path)
#     except ImportError:
#         # If imports fail, use cloud message
#         return "🔧 **Setup Required:** \n\n" + \
#                "To enable voice features:\n" + \
#                "1. Install: `pip install speechrecognition pydub`\n" + \
#                "2. Use our desktop app for automatic setup\n" + \
#                "3. Web version supports text-based AI chat\n\n" + \
#                "💬 **All AI features work via text input!**"







# import speech_recognition as sr
# import mtranslate as mt
# from dotenv import dotenv_values
# import os
# from pydub import AudioSegment
# import tempfile
# import time
# import wave
# import contextlib

# env_vars = dotenv_values(".env")
# InputLanguage = env_vars.get("InputLanguage", "en")

# def QueryModifier(query):
#     if not query or "sorry" in query.lower() or "didn't catch" in query.lower():
#         return "Sorry, I didn't catch that. Could you repeat?"
    
#     new_query = query.lower().strip()
#     query_words = new_query.split()
#     question_words = ["how", "what", "what's", "when", "where", "which", "who", "whom", "whose", "why", "is", "are", "can", "could", "would", "should", "do", "does", "did"]
    
#     if any(word + " " in new_query for word in question_words):
#         if query_words and query_words[-1][-1] in ['.', '?', '!']:
#             new_query = new_query[:-1] + "?"
#         else:
#             new_query += "?"
#     else:
#         if query_words and query_words[-1][-1] in ['.', '?', '!']:
#             new_query = new_query[:-1] + "."
#         else:
#             new_query += "."
#     return new_query.capitalize()

# def UniversalTranslator(Text):
#     english_translation = mt.translate(Text, "en", "auto")
#     return english_translation.capitalize()

# def get_audio_duration(audio_path):
#     """Get duration of audio file in seconds"""
#     try:
#         with contextlib.closing(wave.open(audio_path, 'r')) as f:
#             frames = f.getnframes()
#             rate = f.getframerate()
#             return frames / float(rate)
#     except:
#         return 0

# def SpeechRecognition(audio_path):
#     temp_filename = None
#     try:
#         # Create temporary directory if it doesn't exist
#         os.makedirs("Data", exist_ok=True)
        
#         # Convert to WAV format for better compatibility
#         audio = AudioSegment.from_file(audio_path)
        
#         # Check audio duration - reject if too short
#         duration = len(audio) / 1000.0  # Convert ms to seconds
#         if duration < 0.5:  # Less than 0.5 seconds
#             return "Sorry, I didn't catch that. Could you repeat?"
        
#         # Resample to 16kHz for better recognition
#         audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        
#         # Normalize volume
#         audio = audio.normalize()
        
#         # Create a unique temporary file
#         temp_filename = f"Data/temp_audio_{int(time.time() * 1000)}.wav"
#         audio.export(temp_filename, format="wav")
        
#         recognizer = sr.Recognizer()
#         recognizer.energy_threshold = 300  # Lower for better sensitivity
#         recognizer.dynamic_energy_threshold = True
#         recognizer.pause_threshold = 0.8  # Longer pause threshold
        
#         with sr.AudioFile(temp_filename) as source:
#             # Adjust for ambient noise with longer sample
#             recognizer.adjust_for_ambient_noise(source, duration=1.0)
#             audio_data = recognizer.record(source)
            
#         # Try Google speech recognition with longer timeout
#         text = recognizer.recognize_google(audio_data, language=InputLanguage, show_all=False)
#         text = QueryModifier(text)
        
#         # Clean up temporary file
#         try:
#             if os.path.exists(temp_filename):
#                 os.remove(temp_filename)
#         except:
#             pass
            
#         return text
            
#     except sr.UnknownValueError:
#         # Clean up temporary file
#         try:
#             if temp_filename and os.path.exists(temp_filename):
#                 os.remove(temp_filename)
#         except:
#             pass
#         return "Sorry, I didn't catch that. Could you repeat?"
#     except sr.RequestError as e:
#         print(f"Speech service error: {str(e)}")
#         # Clean up temporary file
#         try:
#             if temp_filename and os.path.exists(temp_filename):
#                 os.remove(temp_filename)
#         except:
#             pass
#         return "Speech service unavailable. Please try text input."
#     except Exception as e:
#         print(f"Speech recognition error: {e}")
#         # Clean up temporary file
#         try:
#             if temp_filename and os.path.exists(temp_filename):
#                 os.remove(temp_filename)
#         except:
#             pass
#         return "Error in speech recognition. Please try again."


#====================Backend only ===================================#

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from dotenv import dotenv_values
# import os
# import mtranslate as mt

# env_vars = dotenv_values(".env")
# InputLanguage = env_vars.get("InputLanguage")

# # --- Moved browser setup INSIDE the function to prevent import crashes ---
# driver = None  # Global variable, but initialized only when needed

# def setup_driver():
#     """Initialize the browser driver only when needed"""
#     global driver
#     if driver is not None:
#         return driver
        
#     # Generate HTML file
#     HtmlCode = '''<!DOCTYPE html>
# <html lang="en">
# <head>
#     <title>Speech Recognition</title>
# </head>
# <body>
#     <button id="start" onclick="startRecognition()">Start Recognition</button>
#     <button id="end" onclick="stopRecognition()">Stop Recognition</button>
#     <p id="output"></p>
#     <script>
#         const output = document.getElementById('output');
#         let recognition;

#         function startRecognition() {
#             recognition = new webkitSpeechRecognition() || new SpeechRecognition();
#             recognition.lang = '';
#             recognition.continuous = true;

#             recognition.onresult = function(event) {
#                 const transcript = event.results[event.results.length - 1][0].transcript;
#                 output.textContent += transcript;
#             };

#             recognition.onend = function() {
#                 recognition.start();
#             };
#             recognition.start();
#         }

#         function stopRecognition() {
#             recognition.stop();
#             output.innerHTML = "";
#         }
#     </script>
# </body>
# </html>'''

#     HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

#     os.makedirs("Data", exist_ok=True)
#     with open(r"Data\Voice.html","w") as f:
#         f.write(HtmlCode)
    
#     current_dir = os.getcwd()
#     Link = f"{current_dir}/Data/Voice.html"

#     # Chrome options setup
#     chrome_options = Options()
#     user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#     chrome_options.add_argument(f'user-agent={user_agent}')
#     chrome_options.add_argument("--use-fake-ui-for-media-stream")
#     chrome_options.add_argument("--use-fake-device-for-media-stream")
#     chrome_options.add_argument("--headless=new")
#     chrome_options.add_argument("--disable-logging")
#     chrome_options.add_argument("--log-level=3")

#     # Initialize driver
#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=chrome_options)
#     return driver

# TempDirPath = rf"{os.getcwd()}/Frontend/Files"

# def SetAssistantStatus(Status):
#     with open(rf"{TempDirPath}/Status.data", "w", encoding="utf-8") as file:
#         file.write(Status)
        
# def QueryModifier(Query):
#     new_query = Query.lower().strip()
#     query_words = new_query.split()
#     question_words = ["how", "what","what's", "when", "where", "which", "who", "whom", "whose", "why", "is", "are", "can", "could", "would", "should", "do", "does", "did"]
    
#     if any(word + " " in new_query for word in question_words):
#         if query_words[-1][-1] in ['.', '?', '!']:
#             new_query = new_query[:-1] + "?"
#         else:
#             new_query += "?"
#     else:
#         if query_words[-1][-1] in ['.', '?', '!']:
#             new_query = new_query[:-1] + "."
#         else:
#             new_query += "."
#     return new_query.capitalize()

# def UniversalTranslator(Text):
#     english_translation = mt.translate(Text, "en", "auto")
#     return english_translation.capitalize()

# def SpeechRecognition():
#     """Main speech recognition function - now initializes driver only when called"""
#     global driver
#     try:
#         if driver is None:
#             driver = setup_driver()
            
#         driver.get("file:///" + os.path.join(os.getcwd(), "Data", "Voice.html"))
#         driver.find_element(by=By.ID, value="start").click()
        
#         while True:
#             try:
#                 Text = driver.find_element(by=By.ID, value="output").text
#                 if Text:
#                     driver.find_element(by=By.ID, value="end").click()
                    
#                     if InputLanguage.lower() != "en" or "en" in InputLanguage.lower():
#                         return QueryModifier(Text)
#                     else:
#                         SetAssistantStatus("Translating...")
#                         return QueryModifier(UniversalTranslator(Text))
#             except Exception as e:
#                 pass
                
#     except Exception as e:
#         print(f"Speech recognition error: {e}")
#         return "Error in speech recognition"

# if __name__ == "__main__":
#     while True:
#         Text = SpeechRecognition()
#         print(Text)



