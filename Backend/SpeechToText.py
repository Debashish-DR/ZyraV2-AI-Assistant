import speech_recognition as sr
import mtranslate as mt
from dotenv import dotenv_values
import os
from pydub import AudioSegment
import tempfile
import time
import wave
import contextlib

env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en")

def QueryModifier(query):
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

def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

def get_audio_duration(audio_path):
    """Get duration of audio file in seconds"""
    try:
        with contextlib.closing(wave.open(audio_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            return frames / float(rate)
    except:
        return 0

def SpeechRecognition(audio_path):
    temp_filename = None
    try:
        # Create temporary directory if it doesn't exist
        os.makedirs("Data", exist_ok=True)
        
        # Convert to WAV format for better compatibility
        audio = AudioSegment.from_file(audio_path)
        
        # Check audio duration - reject if too short
        duration = len(audio) / 1000.0  # Convert ms to seconds
        if duration < 0.5:  # Less than 0.5 seconds
            return "Sorry, I didn't catch that. Could you repeat?"
        
        # Resample to 16kHz for better recognition
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        
        # Normalize volume
        audio = audio.normalize()
        
        # Create a unique temporary file
        temp_filename = f"Data/temp_audio_{int(time.time() * 1000)}.wav"
        audio.export(temp_filename, format="wav")
        
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300  # Lower for better sensitivity
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.8  # Longer pause threshold
        
        with sr.AudioFile(temp_filename) as source:
            # Adjust for ambient noise with longer sample
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
            audio_data = recognizer.record(source)
            
        # Try Google speech recognition with longer timeout
        text = recognizer.recognize_google(audio_data, language=InputLanguage, show_all=False)
        text = QueryModifier(text)
        
        # Clean up temporary file
        try:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
        except:
            pass
            
        return text
            
    except sr.UnknownValueError:
        # Clean up temporary file
        try:
            if temp_filename and os.path.exists(temp_filename):
                os.remove(temp_filename)
        except:
            pass
        return "Sorry, I didn't catch that. Could you repeat?"
    except sr.RequestError as e:
        print(f"Speech service error: {str(e)}")
        # Clean up temporary file
        try:
            if temp_filename and os.path.exists(temp_filename):
                os.remove(temp_filename)
        except:
            pass
        return "Speech service unavailable. Please try text input."
    except Exception as e:
        print(f"Speech recognition error: {e}")
        # Clean up temporary file
        try:
            if temp_filename and os.path.exists(temp_filename):
                os.remove(temp_filename)
        except:
            pass
        return "Error in speech recognition. Please try again."


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



