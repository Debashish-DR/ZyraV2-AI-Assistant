import cohere
import platform  # ADDED for platform detection
from webbrowser import open as webopen
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from groq import Groq
import webbrowser
import subprocess
import keyboard
import os
import pyautogui
import time
import json
import random
import requests
import pythoncom  # ADDED for COM initialization

# ADDED: Platform detection
def is_windows():
    return platform.system().lower() == 'windows'

# ADDED: Conditional imports for Windows only
if is_windows():
    try:
        from AppOpener import close, open as appopen
        from pywhatkit import search, playonyt
    except ImportError as e:
        print(f"[WARNING] {e} – Install via pip for full features.")
        def appopen(app, **kwargs): return f"Simulating open {app} (AppOpener missing)"
        def close(app, **kwargs): return f"Simulating close {app}"
        def playonyt(query): return f"Simulating YouTube play: {query} (pywhatkit missing)"
        def search(query): webbrowser.open(f"https://www.google.com/search?q={query}")
else:
    # ADDED: Mock functions for non-Windows platforms
    def appopen(app, **kwargs): 
        return f"🔒 Windows-only feature: App automation works on Windows devices. Chat and AI features work everywhere! 📱💻"
    def close(app, **kwargs): 
        return f"🔒 Windows-only feature: App automation works on Windows devices. Chat and AI features work everywhere! 📱💻"
    def playonyt(query): 
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return f"Opened YouTube search for: {query}"
    def search(query): 
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Opened Google search for: {query}"

try:
    from Backend.device_manager import get_device_type, get_connection_method
except ImportError:
    def get_device_type():
        return "pc"
    def get_connection_method():
        return "none"

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
CohereAPIKey = env_vars.get("CohereAPIKey")

co = cohere.Client(api_key=CohereAPIKey) if CohereAPIKey else None

classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "O5uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table__webanswers-table", "dDoNo ikb48b gsrt", "sXLaOe", "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None

professional_responses = [
    "Your satisfaction is my top priority. If there's anything else I can assist you with, please don't hesitate to let me know.",
    "I'm at your service for any additional assistance you may require feel free to ask.",
]

messages = []

SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'User')}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]

def load_contacts():
    try:
        with open(r"Data/contacts.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        default_contacts = {
            "maa": "917749963694",
            "papa": "1234567890",
            "brother": "1234567891",
            "sister": "1234567892"
        }
        os.makedirs("Data", exist_ok=True)
        with open(r"Data/contacts.json", "w", encoding="utf-8") as f:
            json.dump(default_contacts, f, indent=4)
        return default_contacts

def get_phone_number(contact_name):
    contacts = load_contacts()
    contact_name = contact_name.lower().strip()
    
    if contact_name in contacts:
        return contacts[contact_name]
    
    for name, number in contacts.items():
        if contact_name in name or name in contact_name:
            return number
    
    return None

def set_volume(level):
    # ADDED: Platform check for volume control
    if not is_windows():
        return "🔒 Volume control available on Windows devices. Chat and AI features work everywhere! 📱💻"
    
    try:
        # Initialize COM for this thread
        pythoncom.CoInitialize()  # ADDED: Proper COM initialization
        
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        scalar = max(0.0, min(1.0, level / 100.0))
        volume.SetMasterVolumeLevelScalar(scalar, None)
        
        # Cleanup COM
        pythoncom.CoUninitialize()  # ADDED: Proper cleanup
        
        return f"Volume set to {level}%"
        
    except ImportError:
        try:
            if level == 0:
                keyboard.press_and_release("volume mute")
                return "Volume muted"
            else:
                keyboard.press_and_release("volume mute")
                presses = int(level / 10)
                for _ in range(presses):
                    keyboard.press_and_release("volume up")
                time.sleep(0.5)
                return f"Volume approximately set to {level}% (install pycaw for exact)"
        except Exception as e2:
            return f"Volume control error: {str(e2)} (Try installing nircmd for better control)"
        
    except Exception as e:
        # Ensure COM is uninitialized even on error
        try:
            pythoncom.CoUninitialize()
        except:
            pass
        return f"Error setting volume: {str(e)}"

def MediaControl(action):
    try:
        # FIXED: Proper media key mapping
        key_map = {
            "play": "playpause",
            "pause": "playpause", 
            "resume": "playpause",
            "next": "nexttrack",
            "previous": "prevtrack",
            "stop": "stop"
        }
        
        if action in key_map:
            pyautogui.press(key_map[action])
            action_word = "played" if action == "play" else "paused" if action == "pause" else action + "ed"
            return f"Media {action_word}"
        else:
            return f"Unknown media action: {action}"
            
    except Exception as e:
        return f"Error controlling media: {str(e)}"

def MobileOpenApp(app_name):
    device_type = get_device_type()
    connection = get_connection_method()
    
    if connection != "adb" or device_type != "mobile":
        return OpenApp(app_name)
    
    try:
        app_map = {
            "whatsapp": "com.whatsapp",
            "instagram": "com.instagram.android",
            "facebook": "com.facebook.katana",
            "chrome": "com.android.chrome",
            "youtube": "com.google.android.youtube",
            "spotify": "com.spotify.music",
            "music": "com.android.music",
            "messages": "com.android.mms",
            "phone": "com.android.dialer",
            "youtube music": "com.google.android.apps.youtube.music"
        }
        
        app_package = app_map.get(app_name.lower(), f"com.{app_name}")
        
        if connection == "adb":
            result = subprocess.run(['adb', 'shell', 'am', 'start', '-n', f'{app_package}/.MainActivity'], 
                                  capture_output=True, text=True, timeout=10)
        else:
            result = subprocess.run(['am', 'start', '-n', f'{app_package}/.MainActivity'], 
                                  capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return f"Opened {app_name} on mobile"
        else:
            return f"Failed to open {app_name}"
            
    except Exception as e:
        return f"Error opening {app_name}: {str(e)}"
    
    return "Mobile function called on non-mobile device"

def MobileCall(contact):
    phone_number = get_phone_number(contact)
    if not phone_number:
        return f"Could not find number for {contact}"
    
    device_type = get_device_type()
    connection = get_connection_method()
    
    if connection != "adb" or device_type != "mobile":
        return CallContact(contact)
    
    try:
        if connection == "adb":
            result = subprocess.run(['adb', 'shell', 'am', 'start', '-a', 'android.intent.action.CALL', '-d', f'tel:{phone_number}'], 
                                  capture_output=True, text=True, timeout=10)
        else:
            result = subprocess.run(['am', 'start', '-a', 'android.intent.action.CALL', '-d', f'tel:{phone_number}'], 
                                  capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return f"Calling {contact}"
        else:
            return f"Call failed to initiate"
            
    except Exception as e:
        return f"Call error: {str(e)}"
    
    return "Mobile function called on non-mobile device"

def MobileSendMessage(contact, message_text=""):
    phone_number = get_phone_number(contact)
    if not phone_number:
        return f"Could not find number for {contact}"
    
    device_type = get_device_type()
    connection = get_connection_method()
    
    if connection != "adb" or device_type != "mobile":
        return SendMessage(contact, message_text)
    
    try:
        if connection == "adb":
            result = subprocess.run(['adb', 'shell', 'am', 'start', '-a', 'android.intent.action.SENDTO', '-d', f'sms:{phone_number}', '--es', 'sms_body', message_text], 
                                  capture_output=True, text=True, timeout=15)
        else:
            result = subprocess.run(['am', 'start', '-a', 'android.intent.action.SENDTO', '-d', f'sms:{phone_number}', '--es', 'sms_body', message_text], 
                                  capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            return f"Message ready to send to {contact}"
        else:
            return f"Message setup failed"
            
    except Exception as e:
        return f"Message error: {str(e)}"
    
    return "Mobile function called on non-mobile device"

def MobilePlayMusic(song_name=""):
    try:
        if not song_name or "music" in song_name.lower():
            subprocess.run(['input', 'keyevent', '85'], timeout=5)
            return "Resuming music playback"
        
        music_apps = [
            'com.spotify.music',
            'com.google.android.apps.youtube.music',
            'com.gaana',
            'com.jio.media.jiobeats',
            'com.apple.android.music'
        ]
        
        for app in music_apps:
            try:
                result = subprocess.run(['am', 'start', '-n', f'{app}/.MainActivity'], 
                                      timeout=10, capture_output=True)
                if result.returncode == 0:
                    time.sleep(3)
                    return f"Opened music app. Please play {song_name}"
            except:
                continue
                
        return "Could not open music app. Please play manually"
        
    except Exception as e:
        return f"Mobile music error: {str(e)}"

def PlayYoutube(query):
    try:
        if is_windows():
            playonyt(query)
            return f"Playing {query} on YouTube"
        else:
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            return f"Opened YouTube search for: {query}"
    except Exception as e:
        return f"Error playing YouTube: {str(e)}"

def PlayMusic(song_name=""):
    device_type = get_device_type()
    
    if device_type == "mobile":
        return MobilePlayMusic(song_name)
    
    try:
        song_name = song_name.replace("on music", "").replace("music", "").replace("on youtube music", "").strip()
        
        if not song_name or "random" in song_name.lower():
            # FIXED: Use proper Microsoft Edge command
            if is_windows():
                os.system('start msedge "https://music.youtube.com/watch?v=uBcdZB3MoCM&list=RDAMVMuBcdZB3MoCM"')
            else:
                webbrowser.open("https://music.youtube.com")
            return "Playing music on YouTube Music"
        else:
            # FIXED: Use webopen instead of playonyt for better reliability
            search_url = f"https://music.youtube.com/search?q={song_name.replace(' ', '+')}"
            webopen(search_url)
            time.sleep(3)  # Wait for page to load
            # Simulate pressing Enter to play first result
            if is_windows():
                pyautogui.press('enter')
            return f"Playing {song_name} on YouTube Music"
            
    except Exception as e:
        return f"Error playing music: {str(e)}"

def PlaySpotify(song_name=""):
    device_type = get_device_type()
    
    if device_type == "mobile":
        return MobileOpenApp("spotify")
    
    try:
        song_name = song_name.replace("on spotify", "").replace("spotify", "").strip().lower()
        
        if not song_name or "music" in song_name.lower():
            webopen("https://open.spotify.com")
            time.sleep(5)
            if is_windows():
                pyautogui.press('space')
            return "Playing music on Spotify"
        else:
            return PlayYoutube(song_name)
            
    except Exception as e:
        return f"Error controlling Spotify: {str(e)}"

def GoogleSearch(Topic):
    from Backend.RealtimeSearchEngine import RealtimeSearchEngine
    return RealtimeSearchEngine(Topic)

def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return f"Searched YouTube for: {Topic}"

def Content(Topic):
    def OpenNotepad(File):
        if is_windows():
            default_text_editor = "notepad.exe"
            subprocess.Popen([default_text_editor, File])
        else:
            # For non-Windows, try to open with default text editor
            try:
                subprocess.Popen(['xdg-open', File])  # Linux
            except:
                try:
                    subprocess.Popen(['open', File])  # macOS
                except:
                    return "Could not open text editor on this platform"
        
    def ContentWriterAI(prompt):
        if not client:
            return "Groq API not configured"
            
        messages.append({"role": "user", "content": f"{prompt}."})
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True,
            stop=None
        )
        
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
                
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer
    
    Topic = Topic.replace("Content ", "")
    ContentByAI = ContentWriterAI(Topic)
    
    os.makedirs("Data", exist_ok=True)
    filename = f"Data/{Topic.lower().replace(' ', '')}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(ContentByAI)
    
    OpenNotepad(filename)
    return f"Created content: {Topic}"

def OpenApp(app_name):
    device_type = get_device_type()
    
    if device_type == "mobile":
        return MobileOpenApp(app_name)
        
    app_name = app_name.lower().strip()
    
    if "youtube music" in app_name or "yt music" in app_name:
        if is_windows():
            os.system('start msedge "https://music.youtube.com"')
        else:
            webbrowser.open("https://music.youtube.com")
        return "Opened YouTube Music"
    
    # ADDED: Platform check for app automation
    if not is_windows():
        website_map = {
            "whatsapp": "https://web.whatsapp.com",
            "instagram": "https://www.instagram.com",
            "facebook": "https://www.facebook.com",
            "telegram": "https://web.telegram.org",
            "spotify": "https://open.spotify.com",
            "netflix": "https://www.netflix.com",
            "twitter": "https://twitter.com",
            "linkedin": "https://www.linkedin.com",
            "youtube": "https://www.youtube.com",
            "gmail": "https://mail.google.com",
            "chrome": "https://www.google.com",
            "discord": "https://discord.com/app",
            "youtube music": "https://music.youtube.com",
            "yt music": "https://music.youtube.com"
        }
        
        if app_name in website_map:
            webopen(website_map[app_name])
            return f"Opened {app_name}"
        return "🔒 App automation works on Windows devices. Chat and AI features work everywhere! 📱💻"
    
    # Windows-specific app opening
    try:
        result = appopen(app_name, throw_error=True, match_closest=True)
        if result:
            return f"Opened {app_name}"
    except Exception as e:
        print(f"App not found locally: {e}")
    
    website_map = {
        "whatsapp": "https://web.whatsapp.com",
        "instagram": "https://www.instagram.com",
        "facebook": "https://www.facebook.com",
        "telegram": "https://web.telegram.org",
        "spotify": "https://open.spotify.com",
        "netflix": "https://www.netflix.com",
        "twitter": "https://twitter.com",
        "linkedin": "https://www.linkedin.com",
        "youtube": "https://www.youtube.com",
        "gmail": "https://mail.google.com",
        "chrome": "https://www.google.com",
        "discord": "https://discord.com/app",
        "youtube music": "https://music.youtube.com",
        "yt music": "https://music.youtube.com"
    }
    
    if app_name in website_map:
        webopen(website_map[app_name])
        return f"Opened {app_name}"
    
    return f"Could not open {app_name}"

def CloseApp(app_name):
    device_type = get_device_type()
    
    if device_type == "mobile":
        return "Close app not supported on mobile"
    
    # ADDED: Platform check for app closing
    if not is_windows():
        return "🔒 App automation works on Windows devices. Chat and AI features work everywhere! 📱💻"
    
    protected_apps = ["python", "vscode", "pycharm", "cmd", "terminal", "assistant", "zyra", "main"]
    
    if any(protected in app_name.lower() for protected in protected_apps):
        return f"Cannot close {app_name} - protected application"
    
    try:
        if any(browser in app_name.lower() for browser in ["chrome", "youtube", "spotify", "web", "browser"]):
            pyautogui.hotkey('ctrl', 'w')
            time.sleep(1)
            return f"Closed {app_name} tab"
        else:
            result = subprocess.run(['taskkill', '/f', '/im', f'{app_name}.exe'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return f"Closed {app_name}"
            else:
                return f"Could not close {app_name}"
                
    except Exception as e:
        return f"Error closing {app_name}: {str(e)}"

def CloseAllTabs():
    device_type = get_device_type()
    
    if device_type == "mobile":
        return "Close all tabs not supported on mobile"
    
    # ADDED: Platform check for tab closing
    if not is_windows():
        return "🔒 App automation works on Windows devices. Chat and AI features work everywhere! 📱💻"
    
    try:
        result = subprocess.run(['tasklist'], capture_output=True, text=True)
        browsers = ['chrome.exe', 'msedge.exe', 'firefox.exe']
        browser_running = any(browser in result.stdout for browser in browsers)
        
        if browser_running:
            pyautogui.hotkey('ctrl', 'shift', 'w')
            time.sleep(1)
            return "All browser tabs closed"
        else:
            return "No browser tabs open to close"
            
    except Exception as e:
        return f"Error closing all tabs: {str(e)}"

def CloseAllWindows():
    device_type = get_device_type()
    
    if device_type == "mobile":
        return "Close all windows not supported on mobile"
    
    # ADDED: Platform check for window closing
    if not is_windows():
        return "🔒 App automation works on Windows devices. Chat and AI features work everywhere! 📱💻"
    
    protected_apps = ["python", "vscode", "pycharm", "cmd", "terminal", "assistant", "zyra", "main"]
    
    try:
        result = subprocess.run(['tasklist'], capture_output=True, text=True)
        processes = result.stdout.lower()
        
        common_apps = ['notepad.exe', 'chrome.exe', 'msedge.exe', 'firefox.exe', 'spotify.exe']
        closed = []
        
        for app in common_apps:
            if app in processes and not any(protected in app for protected in protected_apps):
                subprocess.run(['taskkill', '/f', '/im', app], capture_output=True, text=True, timeout=5)
                closed.append(app)
        
        for _ in range(5):
            pyautogui.hotkey('alt', 'f4')
            time.sleep(0.5)
        
        if closed:
            return f"Closed windows: {', '.join(closed)} and others"
        return "All non-protected windows closed"
        
    except Exception as e:
        return f"Error closing all windows: {str(e)}"

def System(command):
    device_type = get_device_type()
    if device_type == "mobile":
        return "System commands not supported on mobile"
    
    # ADDED: Platform check for system commands
    if not is_windows():
        if any(cmd in command.lower() for cmd in ['close', 'open', 'volume', 'mute', 'shutdown', 'lock', 'restart']):
            return "🔒 System automation works on Windows devices. Chat and AI features work everywhere! 📱💻"
    
    command = command.strip().lower()
    
    if command == "close all tabs":
        return CloseAllTabs()
    elif command == "close all windows":
        return CloseAllWindows()
    
    if command == "shutdown":
        try:
            CloseAllWindows()
            time.sleep(2)
            os.system("shutdown /s /t 10")
            return "Closing all windows and shutting down computer in 10 seconds..."
        except Exception as e:
            return f"Error during shutdown: {str(e)}"
    
    # FIXED: Media control commands
    if command in ["play", "pause", "resume", "next", "previous", "stop"]:
        return MediaControl(command)
    
    if command == "mute":
        return set_volume(0)
    elif command == "unmute":
        return set_volume(50)
    
    if any(word in command for word in ["volume", "vol"]):
        numbers = [int(s) for s in command.split() if s.isdigit()]
        
        if numbers:
            level = min(max(numbers[0], 0), 100)
            return set_volume(level)
        elif "full" in command or "max" in command or "100" in command:
            return set_volume(100)
        elif "up" in command:
            current_vol = 50  # Default assumption
            return set_volume(min(current_vol + 20, 100))
        elif "down" in command:
            current_vol = 50  # Default assumption  
            return set_volume(max(current_vol - 20, 0))
    
    if command == "lock":
        try:
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
            return "PC locked"
        except Exception as e:
            return f"Error locking PC: {e}"
            
    elif command == "restart":
        os.system("shutdown /r /t 1")
        return "Restarting computer..."
    
    return f"Unknown system command: {command}"

def SendMessage(contact, message_text=""):
    device_type = get_device_type()
    if device_type == "mobile":
        return MobileSendMessage(contact, message_text)
    
    try:
        phone_number = get_phone_number(contact)
        if not phone_number:
            phone_number = ''.join(filter(str.isdigit, contact))
        
        if not phone_number:
            webopen("https://web.whatsapp.com")
            return f"Opened WhatsApp. Please search for '{contact}' and send: '{message_text}'"
        
        phone_number = ''.join(filter(str.isdigit, phone_number))
        if len(phone_number) == 10:
            phone_number = '91' + phone_number
        
        encoded_message = requests.utils.quote(message_text)
        whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_message}"
        
        webopen(whatsapp_url)
        time.sleep(4)
        if is_windows():
            pyautogui.press('enter')
        time.sleep(2)
        
        if is_windows():
            pyautogui.hotkey('ctrl', 'w')
        
        return f"Message sent to {contact}"
        
    except Exception as e:
        return f"Error: {str(e)}. Please message manually."

def CallContact(contact):
    device_type = get_device_type()
    if device_type == "mobile":
        return MobileCall(contact)
    
    try:
        phone_number = get_phone_number(contact)
        if not phone_number:
            phone_number = ''.join(filter(str.isdigit, contact))
        
        if not phone_number:
            return f"Could not find phone number for {contact}"
        
        if len(phone_number) == 10:
            phone_number = '91' + phone_number
        
        webopen(f"tel:{phone_number}")
        return f"Calling {contact} ({phone_number})"
        
    except Exception as e:
        return f"Error initiating call: {str(e)}"

def ExecuteCommand(command):
    # FIXED: Handle media control commands properly
    if command in ["play", "pause", "resume", "next", "previous", "stop"]:
        return MediaControl(command)
    
    if command.startswith("open "):
        app_name = command.removeprefix("open ").strip()
        return OpenApp(app_name)
            
    elif command.startswith("close "):
        app_name = command.removeprefix("close ").strip()
        return CloseApp(app_name)
        
    elif command.startswith("play "):
        song_name = command.removeprefix("play ").strip()
        
        if "on spotify" in song_name.lower():
            song_name = song_name.replace("on spotify", "").strip()
            return PlaySpotify(song_name)
        elif "on youtube music" in song_name.lower():
            song_name = song_name.replace("on youtube music", "").strip()
            return PlayMusic(song_name)
        elif "on youtube" in song_name.lower():
            song_name = song_name.replace("on youtube", "").strip()
            return PlayYoutube(song_name)
        elif "on music" in song_name.lower():
            song_name = song_name.replace("on music", "").strip()
            return PlayMusic(song_name)
        elif "music" in song_name.lower() or not song_name:
            return PlayMusic(song_name)
        else:
            return PlayYoutube(song_name)
        
    elif command.startswith("content "):
        return Content(command.removeprefix("content "))
        
    elif command.startswith("google search "):
        return GoogleSearch(command.removeprefix("google search "))
        
    elif command.startswith("youtube search "):
        return YouTubeSearch(command.removeprefix("youtube search "))
        
    elif command.startswith("system "):
        sys_command = command.removeprefix("system ")
        sys_command = sys_command.replace("_", " ").strip()
        return System(sys_command)
        
    elif command.startswith("call "):
        contact = command.removeprefix("call ")
        return CallContact(contact)
        
    elif command.startswith("message "):
        parts = command.removeprefix("message ").split(" ", 1)
        contact = parts[0]
        message_text = parts[1] if len(parts) > 1 else ""
        return SendMessage(contact, message_text)
        
    elif command.startswith("reminder "):
        reminder_data = command.removeprefix("reminder ")
        return f"Reminder set: {reminder_data}"
    
    elif command == "exit":
        return "Exiting assistant"
        
    else:
        return f"Command '{command}' not recognized. Try 'open app' or 'system help'."

def Automation(commands: list[str]):
    results = []
    
    for command in commands:
        try:
            result = ExecuteCommand(command)
            results.append(result)
        except Exception as e:
            error_msg = f"Error executing '{command}': {str(e)}"
            results.append(error_msg)
    
    return results



# ==================== AUTOMATION MODULE (Only Backend) ==================== #

# import cohere
# from AppOpener import close, open as appopen
# from webbrowser import open as webopen
# from pywhatkit import search, playonyt
# from dotenv import dotenv_values
# from bs4 import BeautifulSoup
# from rich import print
# from groq import Groq
# import webbrowser
# import subprocess
# import requests
# import keyboard
# import asyncio
# import os
# import contextlib
# import sys
# import io
# import pyautogui
# import time
# import json
# import random

# # Import device manager
# try:
#     from Backend.device_manager import get_device_type, get_connection_method
# except ImportError:
#     # Fallback if device_manager not found
#     def get_device_type():
#         return "pc"
#     def get_connection_method():
#         return "none"

# # Import guards for optional libs
# try:
#     from AppOpener import close, open as appopen
#     from pywhatkit import search, playonyt
# except ImportError as e:
#     print(f"[WARNING] {e} – Install via pip for full features.")
#     def appopen(app, **kwargs): return f"Simulating open {app} (AppOpener missing)"
#     def close(app, **kwargs): return f"Simulating close {app}"
#     def playonyt(query): return f"Simulating YouTube play: {query} (pywhatkit missing)"
#     def search(query): webbrowser.open(f"https://www.google.com/search?q={query}")

# env_vars = dotenv_values(".env")
# GroqAPIKey = env_vars.get("GroqAPIKey")
# CohereAPIKey = env_vars.get("CohereAPIKey")

# co = cohere.Client(api_key=CohereAPIKey) if CohereAPIKey else None

# classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "O5uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table__webanswers-table", "dDoNo ikb48b gsrt", "sXLaOe", "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

# useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None

# professional_responses = [
#     "Your satisfaction is my top priority. If there's anything else I can assist you with, please don't hesitate to let me know.",
#     "I'm at your service for any additional assistance you may require feel free to ask.",
# ]

# messages = []

# SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'User')}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]

# # ==================== CONTACT DATABASE ====================
# def load_contacts():
#     """Load saved contacts from file"""
#     try:
#         with open(r"Data/contacts.json", "r", encoding="utf-8") as f:
#             return json.load(f)
#     except (FileNotFoundError, json.JSONDecodeError):
#         default_contacts = {
#             "maa": "917749963694",
#             "papa": "1234567890",
#             "brother": "1234567891",
#             "sister": "1234567892"
#         }
#         os.makedirs("Data", exist_ok=True)
#         with open(r"Data/contacts.json", "w", encoding="utf-8") as f:
#             json.dump(default_contacts, f, indent=4)
#         return default_contacts

# def get_phone_number(contact_name):
#     """Get phone number from contact name"""
#     contacts = load_contacts()
#     contact_name = contact_name.lower().strip()
    
#     if contact_name in contacts:
#         return contacts[contact_name]
    
#     for name, number in contacts.items():
#         if contact_name in name or name in contact_name:
#             return number
    
#     return None

# # ==================== PRECISE VOLUME CONTROL ====================
# def set_volume(level):
#     """Set volume to exact percentage using Windows audio control"""
#     try:
#         # First try the precise method with pycaw
#         from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
#         from ctypes import cast, POINTER
#         from comtypes import CLSCTX_ALL
        
#         devices = AudioUtilities.GetSpeakers()
#         interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
#         volume = cast(interface, POINTER(IAudioEndpointVolume))
        
#         # Convert percentage to scalar (0.0 to 1.0)
#         scalar = max(0.0, min(1.0, level / 100.0))
#         volume.SetMasterVolumeLevelScalar(scalar, None)
        
#         return f"Volume set to {level}%"
        
#     except ImportError:
#         # Fallback if pycaw not installed - use keyboard for approximate levels
#         try:
#             if level == 0:
#                 keyboard.press_and_release("volume mute")
#                 return "Volume muted"
#             else:
#                 # Unmute first
#                 keyboard.press_and_release("volume mute")
#                 # Simulate level: e.g., press up multiple times from min (rough, but works without pycaw)
#                 presses = int(level / 10)  # e.g., 50% = 5 presses (adjust based on your system)
#                 for _ in range(presses):
#                     keyboard.press_and_release("volume up")
#                 time.sleep(0.5)  # Brief pause
#                 return f"Volume approximately set to {level}% (install pycaw for exact)"
#         except Exception as e2:
#             return f"Volume control error: {str(e2)} (Try installing nircmd for better control)"
        
#     except Exception as e:
#         return f"Error setting volume: {str(e)}"

# # ==================== IMPROVED MEDIA CONTROL ====================
# def MediaControl(action):
#     """Improved media control - NO auto-pausing, better resume functionality"""
#     # Ensure a media app is focused or open a default
#     if action in ["play", "resume", "pause"]:
#         try:
#             # Check if any media app is running (simple check)
#             result = subprocess.run(['tasklist'], capture_output=True, text=True)
#             if 'spotify.exe' not in result.stdout and 'chrome.exe' not in result.stdout:  # Example check
#                 webopen("https://open.spotify.com")  # Fallback open
#                 time.sleep(2)
#         except:
#             pass  # Silent fallback
#     try:
#         if action == "play" or action == "resume":
#             # Single press only - this will RESUME paused media
#             pyautogui.press('playpause')
#             return "Media resumed"
#         elif action == "pause":
#             # Single press only - this will PAUSE playing media
#             pyautogui.press('playpause')
#             return "Media paused"
#         elif action == "next":
#             pyautogui.press('nexttrack')
#             return "Next track"
#         elif action == "previous":
#             pyautogui.press('prevtrack')
#             return "Previous track"
#     except Exception as e:
#         return f"Error controlling media: {str(e)}"

# # ==================== MOBILE FUNCTIONS ====================
# def MobileOpenApp(app_name):
#     """Open app on mobile device"""
#     device_type = get_device_type()
#     connection = get_connection_method()
    
#     if connection != "adb" or device_type != "mobile":
#         print("[WARNING] No ADB connection. Falling back to PC simulation.")
#         return OpenApp(app_name)  # Simulate on PC
    
#     try:
#         app_map = {
#             "whatsapp": "com.whatsapp",
#             "instagram": "com.instagram.android",
#             "facebook": "com.facebook.katana",
#             "chrome": "com.android.chrome",
#             "youtube": "com.google.android.youtube",
#             "spotify": "com.spotify.music",
#             "music": "com.android.music",
#             "messages": "com.android.mms",
#             "phone": "com.android.dialer",
#             "youtube music": "com.google.android.apps.youtube.music"
#         }
        
#         app_package = app_map.get(app_name.lower(), f"com.{app_name}")
        
#         if connection == "adb":
#             result = subprocess.run(['adb', 'shell', 'am', 'start', '-n', f'{app_package}/.MainActivity'], 
#                                   capture_output=True, text=True, timeout=10)
#         else:
#             result = subprocess.run(['am', 'start', '-n', f'{app_package}/.MainActivity'], 
#                                   capture_output=True, text=True, timeout=10)
        
#         if result.returncode == 0:
#             return f"Opened {app_name} on mobile"
#         else:
#             return f"Failed to open {app_name}"
            
#     except Exception as e:
#         return f"Error opening {app_name}: {str(e)}"
    
#     return "Mobile function called on non-mobile device"

# def MobileCall(contact):
#     """Make call on mobile"""
#     phone_number = get_phone_number(contact)
#     if not phone_number:
#         return f"Could not find number for {contact}"
    
#     device_type = get_device_type()
#     connection = get_connection_method()
    
#     if connection != "adb" or device_type != "mobile":
#         print("[WARNING] No ADB connection. Falling back to PC simulation.")
#         return CallContact(contact)  # Simulate on PC
    
#     try:
#         if connection == "adb":
#             result = subprocess.run(['adb', 'shell', 'am', 'start', '-a', 'android.intent.action.CALL', '-d', f'tel:{phone_number}'], 
#                                   capture_output=True, text=True, timeout=10)
#         else:
#             result = subprocess.run(['am', 'start', '-a', 'android.intent.action.CALL', '-d', f'tel:{phone_number}'], 
#                                   capture_output=True, text=True, timeout=10)
        
#         if result.returncode == 0:
#             return f"Calling {contact}"
#         else:
#             return f"Call failed to initiate"
            
#     except Exception as e:
#         return f"Call error: {str(e)}"
    
#     return "Mobile function called on non-mobile device"

# def MobileSendMessage(contact, message_text=""):
#     """Send message on mobile"""
#     phone_number = get_phone_number(contact)
#     if not phone_number:
#         return f"Could not find number for {contact}"
    
#     device_type = get_device_type()
#     connection = get_connection_method()
    
#     if connection != "adb" or device_type != "mobile":
#         print("[WARNING] No ADB connection. Falling back to PC simulation.")
#         return SendMessage(contact, message_text)  # Simulate on PC
    
#     try:
#         if connection == "adb":
#             result = subprocess.run(['adb', 'shell', 'am', 'start', '-a', 'android.intent.action.SENDTO', '-d', f'sms:{phone_number}', '--es', 'sms_body', message_text], 
#                                   capture_output=True, text=True, timeout=15)
#         else:
#             result = subprocess.run(['am', 'start', '-a', 'android.intent.action.SENDTO', '-d', f'sms:{phone_number}', '--es', 'sms_body', message_text], 
#                                   capture_output=True, text=True, timeout=15)
        
#         if result.returncode == 0:
#             return f"Message ready to send to {contact}"
#         else:
#             return f"Message setup failed"
            
#     except Exception as e:
#         return f"Message error: {str(e)}"
    
#     return "Mobile function called on non-mobile device"

# def MobilePlayMusic(song_name=""):
#     """Mobile music control"""
#     try:
#         if not song_name or "music" in song_name.lower():
#             subprocess.run(['input', 'keyevent', '85'], timeout=5)
#             return "Resuming music playback"
        
#         music_apps = [
#             'com.spotify.music',
#             'com.google.android.apps.youtube.music',
#             'com.gaana',
#             'com.jio.media.jiobeats',
#             'com.apple.android.music'
#         ]
        
#         for app in music_apps:
#             try:
#                 result = subprocess.run(['am', 'start', '-n', f'{app}/.MainActivity'], 
#                                       timeout=10, capture_output=True)
#                 if result.returncode == 0:
#                     time.sleep(3)
#                     return f"Opened music app. Please play {song_name}"
#             except:
#                 continue
                
#         return "Could not open music app. Please play manually"
        
#     except Exception as e:
#         return f"Mobile music error: {str(e)}"

# # ==================== YOUTUBE FUNCTION ====================
# def PlayYoutube(query):
#     """Simple YouTube playback without auto-pausing"""
#     try:
#         playonyt(query)
#         return f"Playing {query} on YouTube"
#     except Exception as e:
#         return f"Error playing YouTube: {str(e)}"

# # ==================== IMPROVED MUSIC FUNCTION ====================
# def PlayMusic(song_name=""):
#     """Play music - YouTube Music on Edge, everything else as before"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         # On mobile, use the original method (Chrome)
#         return MobileOpenApp("youtube music")
    
#     try:
#         song_name = song_name.replace("on music", "").replace("music", "").replace("on youtube music", "").strip()
        
#         if not song_name or "random" in song_name.lower():
#             # ONLY YouTube Music uses Edge - for cleaner audio
#             os.system('start msedge "https://music.youtube.com/watch?v=uBcdZB3MoCM&list=RDAMVMuBcdZB3MoCM"')
#             return "Playing << E Chala Bate >> Odia song on Youtube music..."
#         else:
#             # For specific songs, use the original playonyt with Chrome
#             playonyt(song_name)
#             return f"Playing {song_name} on YouTube"
            
#     except Exception as e:
#         return f"Error playing music: {str(e)}"

# def PlaySpotify(song_name=""):
#     """Spotify control"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return MobileOpenApp("spotify")
    
#     try:
#         song_name = song_name.replace("on spotify", "").replace("spotify", "").strip().lower()
        
#         if not song_name or "music" in song_name.lower():
#             webopen("https://open.spotify.com")
#             time.sleep(5)
#             pyautogui.press('space')
#             return "Playing music on Spotify"
#         else:
#             return PlayYoutube(song_name)
            
#     except Exception as e:
#         return f"Error controlling Spotify: {str(e)}"

# # ==================== BASIC FUNCTIONS ====================
# def GoogleSearch(Topic):
#     """Use the advanced RealtimeSearchEngine instead of just opening browser"""
#     from Backend.RealtimeSearchEngine import RealtimeSearchEngine
#     return RealtimeSearchEngine(Topic)

# def YouTubeSearch(Topic):
#     """Search on YouTube"""
#     Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
#     webbrowser.open(Url4Search)
#     return f"Searched YouTube for: {Topic}"

# def Content(Topic):
#     """Generate and open content in Notepad"""
    
#     def OpenNotepad(File):
#         default_text_editor = "notepad.exe"
#         subprocess.Popen([default_text_editor, File])
        
#     def ContentWriterAI(prompt):
#         if not client:
#             return "Groq API not configured"
            
#         messages.append({"role": "user", "content": f"{prompt}."})
        
#         completion = client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=SystemChatBot + messages,
#             temperature=0.7,
#             max_tokens=2048,
#             top_p=1,
#             stream=True,
#             stop=None
#         )
        
#         Answer = ""
#         for chunk in completion:
#             if chunk.choices[0].delta.content:
#                 Answer += chunk.choices[0].delta.content
                
#         Answer = Answer.replace("</s>", "")
#         messages.append({"role": "assistant", "content": Answer})
#         return Answer
    
#     Topic = Topic.replace("Content ", "")
#     ContentByAI = ContentWriterAI(Topic)
    
#     os.makedirs("Data", exist_ok=True)
#     filename = f"Data/{Topic.lower().replace(' ', '')}.txt"
#     with open(filename, "w", encoding="utf-8") as file:
#         file.write(ContentByAI)
    
#     OpenNotepad(filename)
#     return f"Created content: {Topic}"

# # ==================== APP OPENING FUNCTION ====================
# def OpenApp(app_name, sess=requests.session()):
#     """Open application or website"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return MobileOpenApp(app_name)
        
#     app_name = app_name.lower().strip()
#     print(f"OPENING {app_name.upper()}")
    
#     if "youtube music" in app_name or "yt music" in app_name:
#         # YouTube Music uses Edge
#         os.system('start msedge "https://music.youtube.com"')
#         print("Opening YouTube Music in Microsoft Edge")
#         return "Opened YouTube Music in Microsoft Edge"
    
#     try:
#         result = appopen(app_name, throw_error=True, match_closest=True)
#         if result:
#             return f"Opened {app_name}"
#     except Exception as e:
#         print(f"App not found locally: {e}")
    
#     website_map = {
#         "whatsapp": "https://web.whatsapp.com",
#         "instagram": "https://www.instagram.com",
#         "facebook": "https://www.facebook.com",
#         "telegram": "https://web.telegram.org",
#         "spotify": "https://open.spotify.com",
#         "netflix": "https://www.netflix.com",
#         "twitter": "https://twitter.com",
#         "linkedin": "https://www.linkedin.com",
#         "youtube": "https://www.youtube.com",
#         "gmail": "https://mail.google.com",
#         "chrome": "https://www.google.com",
#         "discord": "https://discord.com/app",
#         "youtube music": "https://music.youtube.com",
#         "yt music": "https://music.youtube.com"
#     }
    
#     if app_name in website_map:
#         webopen(website_map[app_name])
#         print(f"Opening {app_name.upper()} official website")
#         return f"Opened {app_name}"
    
#     return f"Could not open {app_name}"

# # ==================== CLOSE APP FUNCTION ====================
# def CloseApp(app_name):
#     """Close application safely"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return "Close app not supported on mobile"
    
#     protected_apps = ["python", "vscode", "pycharm", "cmd", "terminal", "assistant", "zyra", "main"]
    
#     if any(protected in app_name.lower() for protected in protected_apps):
#         return f"Cannot close {app_name} - protected application"
    
#     print(f"CLOSING {app_name.upper()}")
    
#     try:
#         if any(browser in app_name.lower() for browser in ["chrome", "youtube", "spotify", "web", "browser"]):
#             pyautogui.hotkey('ctrl', 'w')
#             time.sleep(1)
#             return f"Closed {app_name} tab"
#         else:
#             result = subprocess.run(['taskkill', '/f', '/im', f'{app_name}.exe'], 
#                                   capture_output=True, text=True, timeout=10)
#             if result.returncode == 0:
#                 return f"Closed {app_name}"
#             else:
#                 return f"Could not close {app_name}"
                
#     except Exception as e:
#         return f"Error closing {app_name}: {str(e)}"

# # ==================== NEW: CLOSE ALL TABS ====================
# def CloseAllTabs():
#     """Close all tabs in the active browser"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return "Close all tabs not supported on mobile"
    
#     try:
#         # Check if a browser is running
#         result = subprocess.run(['tasklist'], capture_output=True, text=True)
#         browsers = ['chrome.exe', 'msedge.exe', 'firefox.exe']
#         browser_running = any(browser in result.stdout for browser in browsers)
        
#         if browser_running:
#             # Simulate Ctrl+Shift+W to close all tabs (works for Chrome/Edge)
#             pyautogui.hotkey('ctrl', 'shift', 'w')
#             time.sleep(1)
#             return "All browser tabs closed"
#         else:
#             return "No browser tabs open to close"
            
#     except Exception as e:
#         return f"Error closing all tabs: {str(e)}"

# # ==================== NEW: CLOSE ALL WINDOWS ====================
# def CloseAllWindows():
#     """Close all open windows/applications except protected ones"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return "Close all windows not supported on mobile"
    
#     protected_apps = ["python", "vscode", "pycharm", "cmd", "terminal", "assistant", "zyra", "main"]
    
#     try:
#         # Use Alt+F4 to close all non-protected windows
#         # First, get list of running processes
#         result = subprocess.run(['tasklist'], capture_output=True, text=True)
#         processes = result.stdout.lower()
        
#         # Close common apps (not exhaustive, but safe)
#         common_apps = ['notepad.exe', 'chrome.exe', 'msedge.exe', 'firefox.exe', 'spotify.exe']
#         closed = []
        
#         for app in common_apps:
#             if app in processes and not any(protected in app for protected in protected_apps):
#                 subprocess.run(['taskkill', '/f', '/im', app], capture_output=True, text=True, timeout=5)
#                 closed.append(app)
        
#         # Fallback: Use Alt+F4 multiple times for any remaining windows
#         for _ in range(5):  # Arbitrary limit to avoid infinite loop
#             pyautogui.hotkey('alt', 'f4')
#             time.sleep(0.5)
        
#         if closed:
#             return f"Closed windows: {', '.join(closed)} and others"
#         return "All non-protected windows closed"
        
#     except Exception as e:
#         return f"Error closing all windows: {str(e)}"

# # ==================== FIXED SYSTEM CONTROL ====================
# def System(command):
#     """Fixed system control with proper mute handling and close all/shutdown"""
#     device_type = get_device_type()
#     if device_type == "mobile":
#         return "System commands not supported on mobile"
    
#     command = command.strip().lower()
    
#     # Handle new close all commands
#     if command == "close all tabs":
#         return CloseAllTabs()
#     elif command == "close all windows":
#         return CloseAllWindows()
    
#     # Handle shutdown with close all
#     if command == "shutdown":
#         try:
#             # First close all windows
#             CloseAllWindows()
#             time.sleep(2)  # Wait for closure
#             os.system("shutdown /s /t 10")
#             return "Closing all windows and shutting down computer in 10 seconds..."
#         except Exception as e:
#             return f"Error during shutdown: {str(e)}"
    
#     # Handle media controls - "play" now means "resume"
#     if command in ["play", "resume", "pause", "next", "previous"]:
#         return MediaControl(command)
    
#     # Handle mute/unmute specifically
#     if command == "mute":
#         return set_volume(0)
#     elif command == "unmute":
#         return set_volume(50)  # Set to 50% when unmuting
    
#     # Handle volume commands with exact percentages
#     if any(word in command for word in ["volume", "vol"]):
#         numbers = [int(s) for s in command.split() if s.isdigit()]
        
#         if numbers:
#             level = min(max(numbers[0], 0), 100)
#             return set_volume(level)
#         elif "full" in command or "max" in command or "100" in command:
#             return set_volume(100)
#         elif "up" in command:
#             return "Use specific volume level like 'volume 50'"
#         elif "down" in command:
#             return "Use specific volume level like 'volume 30'"
    
#     # Other system commands
#     if command == "lock":
#         try:
#             subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
#             return "PC locked"
#         except Exception as e:
#             return f"Error locking PC: {e}"
            
#     elif command == "restart":
#         os.system("shutdown /r /t 1")
#         return "Restarting computer..."
    
#     return f"Unknown system command: {command}"

# # ==================== WHATSAPP FUNCTION ====================
# def SendMessage(contact, message_text=""):
#     """WhatsApp messaging"""
#     device_type = get_device_type()
#     if device_type == "mobile":
#         return MobileSendMessage(contact, message_text)
    
#     print(f"[MESSAGE] Sending to {contact}: {message_text}")
    
#     try:
#         phone_number = get_phone_number(contact)
#         if not phone_number:
#             phone_number = ''.join(filter(str.isdigit, contact))
        
#         if not phone_number:
#             webopen("https://web.whatsapp.com")
#             return f"Opened WhatsApp. Please search for '{contact}' and send: '{message_text}'"
        
#         phone_number = ''.join(filter(str.isdigit, phone_number))
#         if len(phone_number) == 10:
#             phone_number = '91' + phone_number
        
#         encoded_message = requests.utils.quote(message_text)
#         whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_message}"
        
#         webopen(whatsapp_url)
#         time.sleep(4)
#         pyautogui.press('enter')
#         time.sleep(2)
        
#         pyautogui.hotkey('ctrl', 'w')
        
#         return f"Message sent to {contact}"
        
#     except Exception as e:
#         return f"Error: {str(e)}. Please message manually."

# # ==================== CALLING FUNCTION ====================
# def CallContact(contact):
#     """Calling implementation"""
#     device_type = get_device_type()
#     if device_type == "mobile":
#         return MobileCall(contact)
    
#     print(f"[CALL] Calling: {contact}")
    
#     try:
#         phone_number = get_phone_number(contact)
#         if not phone_number:
#             phone_number = ''.join(filter(str.isdigit, contact))
        
#         if not phone_number:
#             return f"Could not find phone number for {contact}"
        
#         if len(phone_number) == 10:
#             phone_number = '91' + phone_number
        
#         webopen(f"tel:{phone_number}")
#         return f"Calling {contact} ({phone_number})"
        
#     except Exception as e:
#         return f"Error initiating call: {str(e)}"

# # ==================== COMMAND EXECUTION ====================
# async def ExecuteCommand(command):
#     """Execute a single command and return result"""
#     print(f"[AUTOMATION] Processing command: {command}")
    
#     if command in ["play", "resume", "pause", "next", "previous"]:
#         return MediaControl(command)
    
#     if command.startswith("open "):
#         app_name = command.removeprefix("open ").strip()
#         return OpenApp(app_name)
            
#     elif command.startswith("close "):
#         app_name = command.removeprefix("close ").strip()
#         return CloseApp(app_name)
        
#     elif command.startswith("play "):
#         song_name = command.removeprefix("play ").strip()
        
#         if "on spotify" in song_name.lower():
#             song_name = song_name.replace("on spotify", "").strip()
#             return PlaySpotify(song_name)
#         elif "on youtube music" in song_name.lower():
#             song_name = song_name.replace("on youtube music", "").strip()
#             return PlayMusic(song_name)
#         elif "on youtube" in song_name.lower():
#             song_name = song_name.replace("on youtube", "").strip()
#             return PlayYoutube(song_name)
#         elif "on music" in song_name.lower():
#             song_name = song_name.replace("on music", "").strip()
#             return PlayMusic(song_name)
#         elif "music" in song_name.lower() or not song_name:
#             return PlayMusic(song_name)
#         else:
#             return PlayYoutube(song_name)
        
#     elif command.startswith("content "):
#         return Content(command.removeprefix("content "))
        
#     elif command.startswith("google search "):
#         return GoogleSearch(command.removeprefix("google search "))
        
#     elif command.startswith("youtube search "):
#         return YouTubeSearch(command.removeprefix("youtube search "))
        
#     elif command.startswith("system "):
#         sys_command = command.removeprefix("system ")
#         sys_command = sys_command.replace("_", " ").strip()
#         return System(sys_command)
        
#     elif command.startswith("call "):
#         contact = command.removeprefix("call ")
#         return CallContact(contact)
        
#     elif command.startswith("message "):
#         parts = command.removeprefix("message ").split(" ", 1)
#         contact = parts[0]
#         message_text = parts[1] if len(parts) > 1 else ""
#         return SendMessage(contact, message_text)
        
#     elif command.startswith("reminder "):
#         reminder_data = command.removeprefix("reminder ")
#         return f"Reminder set: {reminder_data}"  # TODO: Add scheduler if needed
    
#     elif command == "exit":
#         return "Exiting assistant"
        
#     else:
#         return f"Command '{command}' not recognized. Try 'open app' or 'system help'."

# async def Automation(commands: list[str]):
#     """Main automation function - execute all commands and return results"""
#     results = []
    
#     for command in commands:
#         try:
#             result = await ExecuteCommand(command)
#             results.append(result)
#             print(f"[RESULT] {result}")
#         except Exception as e:
#             error_msg = f"Error executing '{command}': {str(e)}"
#             results.append(error_msg)
#             print(f"[ERROR] {error_msg}")
    
#     return results
        
# if __name__ == "__main__":
#     print("=== Automation.py Test Mode ===")
#     print("This file is meant to be imported, not run directly.")
#     print("To test, run your main application that calls the Automation() function.")





#======================================================================================final

# import cohere
# from AppOpener import close, open as appopen
# from webbrowser import open as webopen
# from pywhatkit import search, playonyt
# from dotenv import dotenv_values
# from bs4 import BeautifulSoup
# from rich import print
# from groq import Groq
# import webbrowser
# import subprocess
# import requests
# import keyboard
# import asyncio
# import os
# import contextlib
# import sys
# import io
# import pyautogui
# import time
# import json
# import random

# # Import device manager
# try:
#     from Backend.device_manager import get_device_type, get_connection_method
# except ImportError:
#     # Fallback if device_manager not found
#     def get_device_type():
#         return "pc"
#     def get_connection_method():
#         return "none"

# env_vars = dotenv_values(".env")
# GroqAPIKey = env_vars.get("GroqAPIKey")
# CohereAPIKey = env_vars.get("CohereAPIKey")

# co = cohere.Client(api_key=CohereAPIKey) if CohereAPIKey else None

# classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "O5uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table__webanswers-table", "dDoNo ikb48b gsrt", "sXLaOe", "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

# useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None

# professional_responses = [
#     "Your satisfaction is my top priority. If there's anything else I can assist you with, please don't hesitate to let me know.",
#     "I'm at your service for any additional assistance you may require feel free to ask.",
# ]

# messages = []

# SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'User')}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]

# # ==================== CONTACT DATABASE ====================
# def load_contacts():
#     """Load saved contacts from file"""
#     try:
#         with open(r"Data/contacts.json", "r", encoding="utf-8") as f:
#             return json.load(f)
#     except (FileNotFoundError, json.JSONDecodeError):
#         default_contacts = {
#             "maa": "917749963694",
#             "papa": "1234567890",
#             "brother": "1234567891",
#             "sister": "1234567892"
#         }
#         os.makedirs("Data", exist_ok=True)
#         with open(r"Data/contacts.json", "w", encoding="utf-8") as f:
#             json.dump(default_contacts, f, indent=4)
#         return default_contacts

# def get_phone_number(contact_name):
#     """Get phone number from contact name"""
#     contacts = load_contacts()
#     contact_name = contact_name.lower().strip()
    
#     if contact_name in contacts:
#         return contacts[contact_name]
    
#     for name, number in contacts.items():
#         if contact_name in name or name in contact_name:
#             return number
    
#     return None

# # ==================== PRECISE VOLUME CONTROL ====================
# def set_volume(level):
#     """Set volume to exact percentage using Windows audio control"""
#     try:
#         # First try the precise method with pycaw
#         from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
#         from ctypes import cast, POINTER
#         from comtypes import CLSCTX_ALL
        
#         devices = AudioUtilities.GetSpeakers()
#         interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
#         volume = cast(interface, POINTER(IAudioEndpointVolume))
        
#         # Convert percentage to scalar (0.0 to 1.0)
#         scalar = max(0.0, min(1.0, level / 100.0))
#         volume.SetMasterVolumeLevelScalar(scalar, None)
        
#         return f"Volume set to {level}%"
        
#     except ImportError:
#         # Fallback if pycaw not installed
#         try:
#             if level == 0:
#                 for _ in range(2):
#                     keyboard.press_and_release("volume mute")
#                 return "Volume muted"
#             else:
#                 # First ensure not muted
#                 for _ in range(2):
#                     keyboard.press_and_release("volume mute")
                
#                 # For fallback, set to approximate level
#                 keyboard.press_and_release("volume up")
#                 return f"Volume adjusted (install pycaw for exact control)"
                
#         except Exception as e2:
#             return f"Volume control error: {str(e2)}"
        
#     except Exception as e:
#         return f"Error setting volume: {str(e)}"

# # ==================== IMPROVED MEDIA CONTROL ====================
# def MediaControl(action):
#     """Improved media control - NO auto-pausing, better resume functionality"""
#     try:
#         if action == "play" or action == "resume":
#             # Single press only - this will RESUME paused media
#             pyautogui.press('playpause')
#             return "Media resumed"
#         elif action == "pause":
#             # Single press only - this will PAUSE playing media
#             pyautogui.press('playpause')
#             return "Media paused"
#         elif action == "next":
#             pyautogui.press('nexttrack')
#             return "Next track"
#         elif action == "previous":
#             pyautogui.press('prevtrack')
#             return "Previous track"
#     except Exception as e:
#         return f"Error controlling media: {str(e)}"

# # ==================== MOBILE FUNCTIONS ====================
# def MobileOpenApp(app_name):
#     """Open app on mobile device"""
#     device_type = get_device_type()
#     connection = get_connection_method()
    
#     if device_type == "mobile" or connection == "adb":
#         try:
#             app_map = {
#                 "whatsapp": "com.whatsapp",
#                 "instagram": "com.instagram.android",
#                 "facebook": "com.facebook.katana",
#                 "chrome": "com.android.chrome",
#                 "youtube": "com.google.android.youtube",
#                 "spotify": "com.spotify.music",
#                 "music": "com.android.music",
#                 "messages": "com.android.mms",
#                 "phone": "com.android.dialer",
#                 "youtube music": "com.google.android.apps.youtube.music"
#             }
            
#             app_package = app_map.get(app_name.lower(), f"com.{app_name}")
            
#             if connection == "adb":
#                 result = subprocess.run(['adb', 'shell', 'am', 'start', '-n', f'{app_package}/.MainActivity'], 
#                                       capture_output=True, text=True, timeout=10)
#             else:
#                 result = subprocess.run(['am', 'start', '-n', f'{app_package}/.MainActivity'], 
#                                       capture_output=True, text=True, timeout=10)
            
#             if result.returncode == 0:
#                 return f"Opened {app_name} on mobile"
#             else:
#                 return f"Failed to open {app_name}"
                
#         except Exception as e:
#             return f"Error opening {app_name}: {str(e)}"
    
#     return "Mobile function called on non-mobile device"

# def MobileCall(contact):
#     """Make call on mobile"""
#     phone_number = get_phone_number(contact)
#     if not phone_number:
#         return f"Could not find number for {contact}"
    
#     device_type = get_device_type()
#     connection = get_connection_method()
    
#     if device_type == "mobile" or connection == "adb":
#         try:
#             if connection == "adb":
#                 result = subprocess.run(['adb', 'shell', 'am', 'start', '-a', 'android.intent.action.CALL', '-d', f'tel:{phone_number}'], 
#                                       capture_output=True, text=True, timeout=10)
#             else:
#                 result = subprocess.run(['am', 'start', '-a', 'android.intent.action.CALL', '-d', f'tel:{phone_number}'], 
#                                       capture_output=True, text=True, timeout=10)
            
#             if result.returncode == 0:
#                 return f"Calling {contact}"
#             else:
#                 return f"Call failed to initiate"
                
#         except Exception as e:
#             return f"Call error: {str(e)}"
    
#     return "Mobile function called on non-mobile device"

# def MobileSendMessage(contact, message_text=""):
#     """Send message on mobile"""
#     phone_number = get_phone_number(contact)
#     if not phone_number:
#         return f"Could not find number for {contact}"
    
#     device_type = get_device_type()
#     connection = get_connection_method()
    
#     if device_type == "mobile" or connection == "adb":
#         try:
#             if connection == "adb":
#                 result = subprocess.run(['adb', 'shell', 'am', 'start', '-a', 'android.intent.action.SENDTO', '-d', f'sms:{phone_number}', '--es', 'sms_body', message_text], 
#                                       capture_output=True, text=True, timeout=15)
#             else:
#                 result = subprocess.run(['am', 'start', '-a', 'android.intent.action.SENDTO', '-d', f'sms:{phone_number}', '--es', 'sms_body', message_text], 
#                                       capture_output=True, text=True, timeout=15)
            
#             if result.returncode == 0:
#                 return f"Message ready to send to {contact}"
#             else:
#                 return f"Message setup failed"
                
#         except Exception as e:
#             return f"Message error: {str(e)}"
    
#     return "Mobile function called on non-mobile device"

# def MobilePlayMusic(song_name=""):
#     """Mobile music control"""
#     try:
#         if not song_name or "music" in song_name.lower():
#             subprocess.run(['input', 'keyevent', '85'], timeout=5)
#             return "Resuming music playback"
        
#         music_apps = [
#             'com.spotify.music',
#             'com.google.android.apps.youtube.music',
#             'com.gaana',
#             'com.jio.media.jiobeats',
#             'com.apple.android.music'
#         ]
        
#         for app in music_apps:
#             try:
#                 result = subprocess.run(['am', 'start', '-n', f'{app}/.MainActivity'], 
#                                       timeout=10, capture_output=True)
#                 if result.returncode == 0:
#                     time.sleep(3)
#                     return f"Opened music app. Please play {song_name}"
#             except:
#                 continue
                
#         return "Could not open music app. Please play manually"
        
#     except Exception as e:
#         return f"Mobile music error: {str(e)}"

# # ==================== YOUTUBE FUNCTION ====================
# def PlayYoutube(query):
#     """Simple YouTube playback without auto-pausing"""
#     try:
#         playonyt(query)
#         return f"Playing {query} on YouTube"
#     except Exception as e:
#         return f"Error playing YouTube: {str(e)}"

# # ==================== IMPROVED MUSIC FUNCTION ====================
# def PlayMusic(song_name=""):
#     """Play music - YouTube Music on Edge, everything else as before"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         # On mobile, use the original method (Chrome)
#         return MobileOpenApp("youtube music")
    
#     try:
#         song_name = song_name.replace("on music", "").replace("music", "").replace("on youtube music", "").strip()
        
#         if not song_name or "random" in song_name.lower():
#             # ONLY YouTube Music uses Edge - for cleaner audio
#             os.system('start msedge "https://music.youtube.com/watch?v=uBcdZB3MoCM&list=RDAMVMuBcdZB3MoCM"')
#             return "Playing << E Chala Bate >> Odia song on Youtube music..."
#         else:
#             # For specific songs, use the original playonyt with Chrome
#             playonyt(song_name)
#             return f"Playing {song_name} on YouTube"
            
#     except Exception as e:
#         return f"Error playing music: {str(e)}"

# def PlaySpotify(song_name=""):
#     """Spotify control"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return MobileOpenApp("spotify")
    
#     try:
#         song_name = song_name.replace("on spotify", "").replace("spotify", "").strip().lower()
        
#         if not song_name or "music" in song_name.lower():
#             webopen("https://open.spotify.com")
#             time.sleep(5)
#             pyautogui.press('space')
#             return "Playing music on Spotify"
#         else:
#             return PlayYoutube(song_name)
            
#     except Exception as e:
#         return f"Error controlling Spotify: {str(e)}"

# # ==================== BASIC FUNCTIONS ====================
# def GoogleSearch(Topic):
#     """Use the advanced RealtimeSearchEngine instead of just opening browser"""
#     from Backend.RealtimeSearchEngine import RealtimeSearchEngine
#     return RealtimeSearchEngine(Topic)

# def YouTubeSearch(Topic):
#     """Search on YouTube"""
#     Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
#     webbrowser.open(Url4Search)
#     return f"Searched YouTube for: {Topic}"

# def Content(Topic):
#     """Generate and open content in Notepad"""
    
#     def OpenNotepad(File):
#         default_text_editor = "notepad.exe"
#         subprocess.Popen([default_text_editor, File])
        
#     def ContentWriterAI(prompt):
#         if not client:
#             return "Groq API not configured"
            
#         messages.append({"role": "user", "content": f"{prompt}."})
        
#         completion = client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=SystemChatBot + messages,
#             temperature=0.7,
#             max_tokens=2048,
#             top_p=1,
#             stream=True,
#             stop=None
#         )
        
#         Answer = ""
#         for chunk in completion:
#             if chunk.choices[0].delta.content:
#                 Answer += chunk.choices[0].delta.content
                
#         Answer = Answer.replace("</s>", "")
#         messages.append({"role": "assistant", "content": Answer})
#         return Answer
    
#     Topic = Topic.replace("Content ", "")
#     ContentByAI = ContentWriterAI(Topic)
    
#     os.makedirs("Data", exist_ok=True)
#     filename = f"Data/{Topic.lower().replace(' ', '')}.txt"
#     with open(filename, "w", encoding="utf-8") as file:
#         file.write(ContentByAI)
    
#     OpenNotepad(filename)
#     return f"Created content: {Topic}"

# # ==================== APP OPENING FUNCTION ====================
# def OpenApp(app_name, sess=requests.session()):
#     """Open application or website"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return MobileOpenApp(app_name)
        
#     app_name = app_name.lower().strip()
#     print(f"OPENING {app_name.upper()}")
    
#     if "youtube music" in app_name or "yt music" in app_name:
#         # YouTube Music uses Edge
#         os.system('start msedge "https://music.youtube.com"')
#         print("Opening YouTube Music in Microsoft Edge")
#         return "Opened YouTube Music in Microsoft Edge"
    
#     try:
#         result = appopen(app_name, throw_error=True, match_closest=True)
#         if result:
#             return f"Opened {app_name}"
#     except Exception as e:
#         print(f"App not found locally: {e}")
    
#     website_map = {
#         "whatsapp": "https://web.whatsapp.com",
#         "instagram": "https://www.instagram.com",
#         "facebook": "https://www.facebook.com",
#         "telegram": "https://web.telegram.org",
#         "spotify": "https://open.spotify.com",
#         "netflix": "https://www.netflix.com",
#         "twitter": "https://twitter.com",
#         "linkedin": "https://www.linkedin.com",
#         "youtube": "https://www.youtube.com",
#         "gmail": "https://mail.google.com",
#         "chrome": "https://www.google.com",
#         "discord": "https://discord.com/app",
#         "youtube music": "https://music.youtube.com",
#         "yt music": "https://music.youtube.com"
#     }
    
#     if app_name in website_map:
#         webopen(website_map[app_name])
#         print(f"Opening {app_name.upper()} official website")
#         return f"Opened {app_name}"
    
#     return f"Could not open {app_name}"

# # ==================== CLOSE APP FUNCTION ====================
# def CloseApp(app_name):
#     """Close application safely"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return "Close app not supported on mobile"
    
#     protected_apps = ["python", "vscode", "pycharm", "cmd", "terminal", "assistant", "zyra", "main"]
    
#     if any(protected in app_name.lower() for protected in protected_apps):
#         return f"Cannot close {app_name} - protected application"
    
#     print(f"CLOSING {app_name.upper()}")
    
#     try:
#         if any(browser in app_name.lower() for browser in ["chrome", "youtube", "spotify", "web", "browser"]):
#             pyautogui.hotkey('ctrl', 'w')
#             time.sleep(1)
#             return f"Closed {app_name} tab"
#         else:
#             result = subprocess.run(['taskkill', '/f', '/im', f'{app_name}.exe'], 
#                                   capture_output=True, text=True, timeout=10)
#             if result.returncode == 0:
#                 return f"Closed {app_name}"
#             else:
#                 return f"Could not close {app_name}"
                
#     except Exception as e:
#         return f"Error closing {app_name}: {str(e)}"

# # ==================== FIXED SYSTEM CONTROL ====================
# def System(command):
#     """Fixed system control with proper mute handling"""
#     device_type = get_device_type()
#     if device_type == "mobile":
#         return "System commands not supported on mobile"
    
#     command = command.strip().lower()
    
#     # Handle media controls - "play" now means "resume"
#     if command in ["play", "resume", "pause", "next", "previous"]:
#         return MediaControl(command)
    
#     # Handle mute/unmute specifically
#     if command == "mute":
#         return set_volume(0)
#     elif command == "unmute":
#         return set_volume(50)  # Set to 50% when unmuting
    
#     # Handle volume commands with exact percentages
#     if any(word in command for word in ["volume", "vol"]):
#         numbers = [int(s) for s in command.split() if s.isdigit()]
        
#         if numbers:
#             level = min(max(numbers[0], 0), 100)
#             return set_volume(level)
#         elif "full" in command or "max" in command or "100" in command:
#             return set_volume(100)
#         elif "up" in command:
#             return "Use specific volume level like 'volume 50'"
#         elif "down" in command:
#             return "Use specific volume level like 'volume 30'"
    
#     # Other system commands
#     if command == "lock":
#         try:
#             subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
#             return "PC locked"
#         except Exception as e:
#             return f"Error locking PC: {e}"
            
#     elif command == "shutdown":
#         os.system("shutdown /s /t 10")
#         return "Shutting down computer in 10 seconds..."
            
#     elif command == "restart":
#         os.system("shutdown /r /t 1")
#         return "Restarting computer..."
    
#     return f"Unknown system command: {command}"

# # ==================== WHATSAPP FUNCTION ====================
# def SendMessage(contact, message_text=""):
#     """WhatsApp messaging"""
#     device_type = get_device_type()
#     if device_type == "mobile":
#         return MobileSendMessage(contact, message_text)
    
#     print(f"[MESSAGE] Sending to {contact}: {message_text}")
    
#     try:
#         phone_number = get_phone_number(contact)
#         if not phone_number:
#             phone_number = ''.join(filter(str.isdigit, contact))
        
#         if not phone_number:
#             webopen("https://web.whatsapp.com")
#             return f"Opened WhatsApp. Please search for '{contact}' and send: '{message_text}'"
        
#         phone_number = ''.join(filter(str.isdigit, phone_number))
#         if len(phone_number) == 10:
#             phone_number = '91' + phone_number
        
#         encoded_message = requests.utils.quote(message_text)
#         whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_message}"
        
#         webopen(whatsapp_url)
#         time.sleep(4)
#         pyautogui.press('enter')
#         time.sleep(2)
        
#         pyautogui.hotkey('ctrl', 'w')
        
#         return f"Message sent to {contact}"
        
#     except Exception as e:
#         return f"Error: {str(e)}. Please message manually."

# # ==================== CALLING FUNCTION ====================
# def CallContact(contact):
#     """Calling implementation"""
#     device_type = get_device_type()
#     if device_type == "mobile":
#         return MobileCall(contact)
    
#     print(f"[CALL] Calling: {contact}")
    
#     try:
#         phone_number = get_phone_number(contact)
#         if not phone_number:
#             phone_number = ''.join(filter(str.isdigit, contact))
        
#         if not phone_number:
#             return f"Could not find phone number for {contact}"
        
#         if len(phone_number) == 10:
#             phone_number = '91' + phone_number
        
#         webopen(f"tel:{phone_number}")
#         return f"Calling {contact} ({phone_number})"
        
#     except Exception as e:
#         return f"Error initiating call: {str(e)}"

# # ==================== COMMAND EXECUTION ====================
# async def ExecuteCommand(command):
#     """Execute a single command and return result"""
#     print(f"[AUTOMATION] Processing command: {command}")
    
#     if command in ["play", "resume", "pause", "next", "previous"]:
#         return MediaControl(command)
    
#     if command.startswith("open "):
#         app_name = command.removeprefix("open ").strip()
#         return OpenApp(app_name)
            
#     elif command.startswith("close "):
#         app_name = command.removeprefix("close ").strip()
#         return CloseApp(app_name)
        
#     elif command.startswith("play "):
#         song_name = command.removeprefix("play ").strip()
        
#         if "on spotify" in song_name.lower():
#             song_name = song_name.replace("on spotify", "").strip()
#             return PlaySpotify(song_name)
#         elif "on youtube music" in song_name.lower():
#             song_name = song_name.replace("on youtube music", "").strip()
#             return PlayMusic(song_name)
#         elif "on youtube" in song_name.lower():
#             song_name = song_name.replace("on youtube", "").strip()
#             return PlayYoutube(song_name)
#         elif "on music" in song_name.lower():
#             song_name = song_name.replace("on music", "").strip()
#             return PlayMusic(song_name)
#         elif "music" in song_name.lower() or not song_name:
#             return PlayMusic(song_name)
#         else:
#             return PlayYoutube(song_name)
        
#     elif command.startswith("content "):
#         return Content(command.removeprefix("content "))
        
#     elif command.startswith("google search "):
#         return GoogleSearch(command.removeprefix("google search "))
        
#     elif command.startswith("youtube search "):
#         return YouTubeSearch(command.removeprefix("youtube search "))
        
#     elif command.startswith("system "):
#         sys_command = command.removeprefix("system ")
#         sys_command = sys_command.replace("_", " ").strip()
#         return System(sys_command)
        
#     elif command.startswith("call "):
#         contact = command.removeprefix("call ")
#         return CallContact(contact)
        
#     elif command.startswith("message "):
#         parts = command.removeprefix("message ").split(" ", 1)
#         contact = parts[0]
#         message_text = parts[1] if len(parts) > 1 else ""
#         return SendMessage(contact, message_text)
        
#     elif command == "exit":
#         return "Exiting assistant"
        
#     else:
#         return f"No function found for: {command}"

# async def Automation(commands: list[str]):
#     """Main automation function - execute all commands and return results"""
#     results = []
    
#     for command in commands:
#         try:
#             result = await ExecuteCommand(command)
#             results.append(result)
#             print(f"[RESULT] {result}")
#         except Exception as e:
#             error_msg = f"Error executing '{command}': {str(e)}"
#             results.append(error_msg)
#             print(f"[ERROR] {error_msg}")
    
#     return results
        
# if __name__ == "__main__":
#     print("=== Automation.py Test Mode ===")
#     print("This file is meant to be imported, not run directly.")
#     print("To test, run your main application that calls the Automation() function.")








# ==========================================================================================================================================
# import cohere
# from AppOpener import close, open as appopen
# from webbrowser import open as webopen
# from pywhatkit import search, playonyt
# from dotenv import dotenv_values
# from bs4 import BeautifulSoup
# from rich import print
# from groq import Groq
# import webbrowser
# import subprocess
# import requests
# import keyboard
# import asyncio
# import os
# import contextlib
# import sys
# import io
# import pyautogui
# import time
# import json
# import random

# # Import device manager
# try:
#     from Backend.device_manager import get_device_type, get_connection_method
# except ImportError:
#     # Fallback if device_manager not found
#     def get_device_type():
#         return "pc"
#     def get_connection_method():
#         return "none"

# env_vars = dotenv_values(".env")
# GroqAPIKey = env_vars.get("GroqAPIKey")
# CohereAPIKey = env_vars.get("CohereAPIKey")

# co = cohere.Client(api_key=CohereAPIKey) if CohereAPIKey else None

# classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "O5uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table__webanswers-table", "dDoNo ikb48b gsrt", "sXLaOe", "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

# useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None

# professional_responses = [
#     "Your satisfaction is my top priority. If there's anything else I can assist you with, please don't hesitate to let me know.",
#     "I'm at your service for any additional assistance you may require feel free to ask.",
# ]

# messages = []

# SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'User')}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]

# # ==================== CROSS-PLATFORM BROWSER FUNCTIONS ====================
# def open_in_browser(url, description=""):
#     """Smart function that opens URLs in appropriate browser based on device"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         # For mobile, use appropriate mobile method
#         try:
#             connection = get_connection_method()
#             if connection == "adb":
#                 result = subprocess.run(['adb', 'shell', 'am', 'start', '-a', 'android.intent.action.VIEW', '-d', url], 
#                                       timeout=10, capture_output=True, text=True)
#             else:
#                 result = subprocess.run(['am', 'start', '-a', 'android.intent.action.VIEW', '-d', url], 
#                                       timeout=10, capture_output=True, text=True)
            
#             if result.returncode == 0:
#                 return f"Opening {description} on mobile"
#             return f"Could not open {description} on mobile"
                
#         except Exception as e:
#             return f"Mobile browser error: {str(e)}"
#     else:
#         # PC: Use Microsoft Edge to avoid Chrome audio conflicts
#         try:
#             os.system(f'start msedge "{url}"')
#             return f"Opening {description} in Microsoft Edge"
#         except Exception as e:
#             return f"Edge browser error: {str(e)}"

# # ==================== CONTACT DATABASE ====================
# def load_contacts():
#     """Load saved contacts from file"""
#     try:
#         with open(r"Data/contacts.json", "r", encoding="utf-8") as f:
#             return json.load(f)
#     except (FileNotFoundError, json.JSONDecodeError):
#         default_contacts = {
#             "maa": "917749963694",
#             "papa": "1234567890",
#             "brother": "1234567891",
#             "sister": "1234567892"
#         }
#         os.makedirs("Data", exist_ok=True)
#         with open(r"Data/contacts.json", "w", encoding="utf-8") as f:
#             json.dump(default_contacts, f, indent=4)
#         return default_contacts

# def get_phone_number(contact_name):
#     """Get phone number from contact name"""
#     contacts = load_contacts()
#     contact_name = contact_name.lower().strip()
    
#     if contact_name in contacts:
#         return contacts[contact_name]
    
#     for name, number in contacts.items():
#         if contact_name in name or name in contact_name:
#             return number
    
#     return None

# # ==================== PRECISE VOLUME CONTROL ====================
# def set_volume(level):
#     """Set volume to exact percentage using Windows audio control"""
#     try:
#         # First try the precise method with pycaw
#         from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
#         from ctypes import cast, POINTER
#         from comtypes import CLSCTX_ALL
        
#         devices = AudioUtilities.GetSpeakers()
#         interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
#         volume = cast(interface, POINTER(IAudioEndpointVolume))
        
#         # Convert percentage to scalar (0.0 to 1.0)
#         scalar = max(0.0, min(1.0, level / 100.0))
#         volume.SetMasterVolumeLevelScalar(scalar, None)
        
#         return f"Volume set to {level}%"
        
#     except ImportError:
#         # Fallback if pycaw not installed
#         try:
#             if level == 0:
#                 for _ in range(2):
#                     keyboard.press_and_release("volume mute")
#                 return "Volume muted"
#             else:
#                 # First ensure not muted
#                 for _ in range(2):
#                     keyboard.press_and_release("volume mute")
                
#                 # For fallback, set to approximate level
#                 keyboard.press_and_release("volume up")
#                 return f"Volume adjusted (install pycaw for exact control)"
                
#         except Exception as e2:
#             return f"Volume control error: {str(e2)}"
        
#     except Exception as e:
#         return f"Error setting volume: {str(e)}"

# # ==================== IMPROVED MEDIA CONTROL ====================
# def MediaControl(action):
#     """Improved media control - NO auto-pausing, better resume functionality"""
#     try:
#         if action == "play" or action == "resume":
#             # Single press only - this will RESUME paused media
#             pyautogui.press('playpause')
#             return "Media resumed"
#         elif action == "pause":
#             # Single press only - this will PAUSE playing media
#             pyautogui.press('playpause')
#             return "Media paused"
#         elif action == "next":
#             pyautogui.press('nexttrack')
#             return "Next track"
#         elif action == "previous":
#             pyautogui.press('prevtrack')
#             return "Previous track"
#     except Exception as e:
#         return f"Error controlling media: {str(e)}"

# # ==================== MOBILE FUNCTIONS ====================
# def MobileOpenApp(app_name):
#     """Open app on mobile device"""
#     device_type = get_device_type()
#     connection = get_connection_method()
    
#     if device_type == "mobile" or connection == "adb":
#         try:
#             app_map = {
#                 "whatsapp": "com.whatsapp",
#                 "instagram": "com.instagram.android",
#                 "facebook": "com.facebook.katana",
#                 "chrome": "com.android.chrome",
#                 "youtube": "com.google.android.youtube",
#                 "spotify": "com.spotify.music",
#                 "music": "com.android.music",
#                 "messages": "com.android.mms",
#                 "phone": "com.android.dialer",
#                 "youtube music": "com.google.android.apps.youtube.music"
#             }
            
#             app_package = app_map.get(app_name.lower(), f"com.{app_name}")
            
#             if connection == "adb":
#                 result = subprocess.run(['adb', 'shell', 'am', 'start', '-n', f'{app_package}/.MainActivity'], 
#                                       capture_output=True, text=True, timeout=10)
#             else:
#                 result = subprocess.run(['am', 'start', '-n', f'{app_package}/.MainActivity'], 
#                                       capture_output=True, text=True, timeout=10)
            
#             if result.returncode == 0:
#                 return f"Opened {app_name} on mobile"
#             else:
#                 return f"Failed to open {app_name}"
                
#         except Exception as e:
#             return f"Error opening {app_name}: {str(e)}"
    
#     return "Mobile function called on non-mobile device"

# def MobileCall(contact):
#     """Make call on mobile"""
#     phone_number = get_phone_number(contact)
#     if not phone_number:
#         return f"Could not find number for {contact}"
    
#     device_type = get_device_type()
#     connection = get_connection_method()
    
#     if device_type == "mobile" or connection == "adb":
#         try:
#             if connection == "adb":
#                 result = subprocess.run(['adb', 'shell', 'am', 'start', '-a', 'android.intent.action.CALL', '-d', f'tel:{phone_number}'], 
#                                       capture_output=True, text=True, timeout=10)
#             else:
#                 result = subprocess.run(['am', 'start', '-a', 'android.intent.action.CALL', '-d', f'tel:{phone_number}'], 
#                                       capture_output=True, text=True, timeout=10)
            
#             if result.returncode == 0:
#                 return f"Calling {contact}"
#             else:
#                 return f"Call failed to initiate"
                
#         except Exception as e:
#             return f"Call error: {str(e)}"
    
#     return "Mobile function called on non-mobile device"

# def MobileSendMessage(contact, message_text=""):
#     """Send message on mobile"""
#     phone_number = get_phone_number(contact)
#     if not phone_number:
#         return f"Could not find number for {contact}"
    
#     device_type = get_device_type()
#     connection = get_connection_method()
    
#     if device_type == "mobile" or connection == "adb":
#         try:
#             if connection == "adb":
#                 result = subprocess.run(['adb', 'shell', 'am', 'start', '-a', 'android.intent.action.SENDTO', '-d', f'sms:{phone_number}', '--es', 'sms_body', message_text], 
#                                       capture_output=True, text=True, timeout=15)
#             else:
#                 result = subprocess.run(['am', 'start', '-a', 'android.intent.action.SENDTO', '-d', f'sms:{phone_number}', '--es', 'sms_body', message_text], 
#                                       capture_output=True, text=True, timeout=15)
            
#             if result.returncode == 0:
#                 return f"Message ready to send to {contact}"
#             else:
#                 return f"Message setup failed"
                
#         except Exception as e:
#             return f"Message error: {str(e)}"
    
#     return "Mobile function called on non-mobile device"

# def MobilePlayMusic(song_name=""):
#     """Mobile music control"""
#     try:
#         if not song_name or "music" in song_name.lower():
#             subprocess.run(['input', 'keyevent', '85'], timeout=5)
#             return "Resuming music playback"
        
#         music_apps = [
#             'com.spotify.music',
#             'com.google.android.apps.youtube.music',
#             'com.gaana',
#             'com.jio.media.jiobeats',
#             'com.apple.android.music'
#         ]
        
#         for app in music_apps:
#             try:
#                 result = subprocess.run(['am', 'start', '-n', f'{app}/.MainActivity'], 
#                                       timeout=10, capture_output=True)
#                 if result.returncode == 0:
#                     time.sleep(3)
#                     return f"Opened music app. Please play {song_name}"
#             except:
#                 continue
                
#         return "Could not open music app. Please play manually"
        
#     except Exception as e:
#         return f"Mobile music error: {str(e)}"

# # ==================== YOUTUBE FUNCTION ====================
# def PlayYoutube(query):
#     """YouTube playback - uses Edge on PC, Chrome on mobile"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         # On mobile, use the mobile function (Chrome)
#         return MobileOpenApp("youtube")
    
#     try:
#         # On PC, use Microsoft Edge with YouTube search
#         search_query = query.replace(" ", "+")
#         youtube_url = f"https://www.youtube.com/results?search_query={search_query}"
#         os.system(f'start msedge "{youtube_url}"')
#         return f"Searching for {query} on YouTube (Microsoft Edge)"
#     except Exception as e:
#         return f"Error playing YouTube: {str(e)}"

# # ==================== IMPROVED MUSIC FUNCTION ====================
# def PlayMusic(song_name=""):
#     """Play music - uses Edge on PC, Chrome on mobile"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return MobileOpenApp("youtube music")
    
#     try:
#         song_name = song_name.replace("on music", "").replace("music", "").replace("on youtube music", "").strip()
        
#         if not song_name or "random" in song_name.lower():
#             # Open YouTube Music with Bollywood playlist in Edge
#             os.system('start msedge "https://music.youtube.com/watch?v=uBcdZB3MoCM&list=RDAMVMuBcdZB3MoCM"')
#             return "Playing Bollywood music on YouTube Music (Microsoft Edge)"
#         else:
#             # For specific songs, search on YouTube using Edge
#             search_query = song_name.replace(" ", "+")
#             youtube_url = f"https://www.youtube.com/results?search_query={search_query}"
#             os.system(f'start msedge "{youtube_url}"')
#             return f"Searching for {song_name} on YouTube (Microsoft Edge)"
            
#     except Exception as e:
#         return f"Error playing music: {str(e)}"

# def PlaySpotify(song_name=""):
#     """Spotify control"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return MobileOpenApp("spotify")
    
#     try:
#         song_name = song_name.replace("on spotify", "").replace("spotify", "").strip().lower()
        
#         if not song_name or "music" in song_name.lower():
#             os.system('start msedge "https://open.spotify.com"')
#             return "Playing music on Spotify (Microsoft Edge)"
#         else:
#             return PlayYoutube(song_name)
            
#     except Exception as e:
#         return f"Error controlling Spotify: {str(e)}"

# # ==================== BASIC FUNCTIONS ====================
# def GoogleSearch(Topic):
#     """Perform a Google search using Edge"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return MobileOpenApp("chrome")
    
#     search_query = Topic.replace(" ", "+")
#     os.system(f'start msedge "https://www.google.com/search?q={search_query}"')
#     return f"Google search for: {Topic} (Microsoft Edge)"

# def YouTubeSearch(Topic):
#     """Search on YouTube using Edge"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return MobileOpenApp("youtube")
    
#     search_query = Topic.replace(" ", "+")
#     os.system(f'start msedge "https://www.youtube.com/results?search_query={search_query}"')
#     return f"YouTube search for: {Topic} (Microsoft Edge)"

# def Content(Topic):
#     """Generate and open content in Notepad"""
    
#     def OpenNotepad(File):
#         default_text_editor = "notepad.exe"
#         subprocess.Popen([default_text_editor, File])
        
#     def ContentWriterAI(prompt):
#         if not client:
#             return "Groq API not configured"
            
#         messages.append({"role": "user", "content": f"{prompt}."})
        
#         completion = client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=SystemChatBot + messages,
#             temperature=0.7,
#             max_tokens=2048,
#             top_p=1,
#             stream=True,
#             stop=None
#         )
        
#         Answer = ""
#         for chunk in completion:
#             if chunk.choices[0].delta.content:
#                 Answer += chunk.choices[0].delta.content
                
#         Answer = Answer.replace("</s>", "")
#         messages.append({"role": "assistant", "content": Answer})
#         return Answer
    
#     Topic = Topic.replace("Content ", "")
#     ContentByAI = ContentWriterAI(Topic)
    
#     os.makedirs("Data", exist_ok=True)
#     filename = f"Data/{Topic.lower().replace(' ', '')}.txt"
#     with open(filename, "w", encoding="utf-8") as file:
#         file.write(ContentByAI)
    
#     OpenNotepad(filename)
#     return f"Created content: {Topic}"

# # ==================== APP OPENING FUNCTION ====================
# def OpenApp(app_name, sess=requests.session()):
#     """Open application or website"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return MobileOpenApp(app_name)
        
#     app_name = app_name.lower().strip()
#     print(f"OPENING {app_name.upper()}")
    
#     # Website mapping - all will open in Edge on PC
#     website_map = {
#         "whatsapp": "https://web.whatsapp.com",
#         "instagram": "https://www.instagram.com",
#         "facebook": "https://www.facebook.com",
#         "telegram": "https://web.telegram.org",
#         "spotify": "https://open.spotify.com",
#         "netflix": "https://www.netflix.com",
#         "twitter": "https://twitter.com",
#         "linkedin": "https://www.linkedin.com",
#         "youtube": "https://www.youtube.com",
#         "gmail": "https://mail.google.com",
#         "chrome": "https://www.google.com",
#         "discord": "https://discord.com/app",
#         "youtube music": "https://music.youtube.com",
#         "yt music": "https://music.youtube.com"
#     }
    
#     if app_name in website_map:
#         os.system(f'start msedge "{website_map[app_name]}"')
#         return f"Opened {app_name} in Microsoft Edge"
    
#     # For local apps, use the original method
#     try:
#         result = appopen(app_name, throw_error=True, match_closest=True)
#         if result:
#             return f"Opened {app_name}"
#     except Exception as e:
#         print(f"App not found locally: {e}")
#         return f"Could not open {app_name}"

# # ==================== CLOSE APP FUNCTION ====================
# def CloseApp(app_name):
#     """Close application safely"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return "Close app not supported on mobile"
    
#     protected_apps = ["python", "vscode", "pycharm", "cmd", "terminal", "assistant", "zyra", "main"]
    
#     if any(protected in app_name.lower() for protected in protected_apps):
#         return f"Cannot close {app_name} - protected application"
    
#     print(f"CLOSING {app_name.upper()}")
    
#     try:
#         if any(browser in app_name.lower() for browser in ["chrome", "youtube", "spotify", "web", "browser"]):
#             pyautogui.hotkey('ctrl', 'w')
#             time.sleep(1)
#             return f"Closed {app_name} tab"
#         else:
#             result = subprocess.run(['taskkill', '/f', '/im', f'{app_name}.exe'], 
#                                   capture_output=True, text=True, timeout=10)
#             if result.returncode == 0:
#                 return f"Closed {app_name}"
#             else:
#                 return f"Could not close {app_name}"
                
#     except Exception as e:
#         return f"Error closing {app_name}: {str(e)}"

# # ==================== FIXED SYSTEM CONTROL ====================
# def System(command):
#     """Fixed system control with proper mute handling"""
#     device_type = get_device_type()
#     if device_type == "mobile":
#         return "System commands not supported on mobile"
    
#     command = command.strip().lower()
    
#     # Handle media controls - "play" now means "resume"
#     if command in ["play", "resume", "pause", "next", "previous"]:
#         return MediaControl(command)
    
#     # Handle mute/unmute specifically
#     if command == "mute":
#         return set_volume(0)
#     elif command == "unmute":
#         return set_volume(50)  # Set to 50% when unmuting
    
#     # Handle volume commands with exact percentages
#     if any(word in command for word in ["volume", "vol"]):
#         numbers = [int(s) for s in command.split() if s.isdigit()]
        
#         if numbers:
#             level = min(max(numbers[0], 0), 100)
#             return set_volume(level)
#         elif "full" in command or "max" in command or "100" in command:
#             return set_volume(100)
#         elif "up" in command:
#             return "Use specific volume level like 'volume 50'"
#         elif "down" in command:
#             return "Use specific volume level like 'volume 30'"
    
#     # Other system commands
#     if command == "lock":
#         try:
#             subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
#             return "PC locked"
#         except Exception as e:
#             return f"Error locking PC: {e}"
            
#     elif command == "shutdown":
#         os.system("shutdown /s /t 10")
#         return "Shutting down computer in 10 seconds..."
            
#     elif command == "restart":
#         os.system("shutdown /r /t 1")
#         return "Restarting computer..."
    
#     return f"Unknown system command: {command}"

# # ==================== WHATSAPP FUNCTION ====================
# def SendMessage(contact, message_text=""):
#     """WhatsApp messaging"""
#     device_type = get_device_type()
#     if device_type == "mobile":
#         return MobileSendMessage(contact, message_text)
    
#     print(f"[MESSAGE] Sending to {contact}: {message_text}")
    
#     try:
#         phone_number = get_phone_number(contact)
#         if not phone_number:
#             phone_number = ''.join(filter(str.isdigit, contact))
        
#         if not phone_number:
#             os.system('start msedge "https://web.whatsapp.com"')
#             return "Opened WhatsApp on Microsoft Edge"
        
#         phone_number = ''.join(filter(str.isdigit, phone_number))
#         if len(phone_number) == 10:
#             phone_number = '91' + phone_number
        
#         encoded_message = requests.utils.quote(message_text)
#         whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_message}"
        
#         os.system(f'start msedge "{whatsapp_url}"')
#         time.sleep(4)
#         pyautogui.press('enter')
#         time.sleep(2)
#         pyautogui.hotkey('ctrl', 'w')
        
#         return f"Message sent to {contact}"
        
#     except Exception as e:
#         return f"Error: {str(e)}. Please message manually."

# # ==================== CALLING FUNCTION ====================
# def CallContact(contact):
#     """Calling implementation"""
#     device_type = get_device_type()
#     if device_type == "mobile":
#         return MobileCall(contact)
    
#     print(f"[CALL] Calling: {contact}")
    
#     try:
#         phone_number = get_phone_number(contact)
#         if not phone_number:
#             phone_number = ''.join(filter(str.isdigit, contact))
        
#         if not phone_number:
#             return f"Could not find phone number for {contact}"
        
#         if len(phone_number) == 10:
#             phone_number = '91' + phone_number
        
#         os.system(f'start msedge "tel:{phone_number}"')
#         return f"Calling {contact} ({phone_number})"
        
#     except Exception as e:
#         return f"Error initiating call: {str(e)}"

# # ==================== COMMAND EXECUTION ====================
# async def ExecuteCommand(command):
#     """Execute a single command and return result"""
#     print(f"[AUTOMATION] Processing command: {command}")
    
#     if command in ["play", "resume", "pause", "next", "previous"]:
#         return MediaControl(command)
    
#     if command.startswith("open "):
#         app_name = command.removeprefix("open ").strip()
#         return OpenApp(app_name)
            
#     elif command.startswith("close "):
#         app_name = command.removeprefix("close ").strip()
#         return CloseApp(app_name)
        
#     elif command.startswith("play "):
#         song_name = command.removeprefix("play ").strip()
        
#         if "on spotify" in song_name.lower():
#             song_name = song_name.replace("on spotify", "").strip()
#             return PlaySpotify(song_name)
#         elif "on youtube music" in song_name.lower():
#             song_name = song_name.replace("on youtube music", "").strip()
#             return PlayMusic(song_name)
#         elif "on youtube" in song_name.lower():
#             song_name = song_name.replace("on youtube", "").strip()
#             return PlayYoutube(song_name)
#         elif "on music" in song_name.lower():
#             song_name = song_name.replace("on music", "").strip()
#             return PlayMusic(song_name)
#         elif "music" in song_name.lower() or not song_name:
#             return PlayMusic(song_name)
#         else:
#             return PlayYoutube(song_name)
        
#     elif command.startswith("content "):
#         return Content(command.removeprefix("content "))
        
#     elif command.startswith("google search "):
#         return GoogleSearch(command.removeprefix("google search "))
        
#     elif command.startswith("youtube search "):
#         return YouTubeSearch(command.removeprefix("youtube search "))
        
#     elif command.startswith("system "):
#         sys_command = command.removeprefix("system ")
#         sys_command = sys_command.replace("_", " ").strip()
#         return System(sys_command)
        
#     elif command.startswith("call "):
#         contact = command.removeprefix("call ")
#         return CallContact(contact)
        
#     elif command.startswith("message "):
#         parts = command.removeprefix("message ").split(" ", 1)
#         contact = parts[0]
#         message_text = parts[1] if len(parts) > 1 else ""
#         return SendMessage(contact, message_text)
        
#     elif command == "exit":
#         return "Exiting assistant"
        
#     else:
#         return f"No function found for: {command}"

# async def Automation(commands: list[str]):
#     """Main automation function - execute all commands and return results"""
#     results = []
    
#     for command in commands:
#         try:
#             result = await ExecuteCommand(command)
#             results.append(result)
#             print(f"[RESULT] {result}")
#         except Exception as e:
#             error_msg = f"Error executing '{command}': {str(e)}"
#             results.append(error_msg)
#             print(f"[ERROR] {error_msg}")
    
#     return results
        
# if __name__ == "__main__":
#     print("=== Automation.py Test Mode ===")
#     print("This file is meant to be imported, not run directly.")
#     print("To test, run your main application that calls the Automation() function.")

# =================================================Used Code==============================================================

# import cohere
# from AppOpener import close, open as appopen
# from webbrowser import open as webopen
# from pywhatkit import search, playonyt
# from dotenv import dotenv_values
# from bs4 import BeautifulSoup
# from rich import print
# from groq import Groq
# import webbrowser
# import subprocess
# import requests
# import keyboard
# import asyncio
# import os
# import contextlib
# import sys
# import io
# import pyautogui
# import time
# import json
# import random

# # Import device manager
# try:
#     from Backend.device_manager import get_device_type, get_connection_method
# except ImportError:
#     # Fallback if device_manager not found
#     def get_device_type():
#         return "pc"
#     def get_connection_method():
#         return "none"

# env_vars = dotenv_values(".env")
# GroqAPIKey = env_vars.get("GroqAPIKey")
# CohereAPIKey = env_vars.get("CohereAPIKey")

# co = cohere.Client(api_key=CohereAPIKey) if CohereAPIKey else None

# classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "O5uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table__webanswers-table", "dDoNo ikb48b gsrt", "sXLaOe", "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

# useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None

# professional_responses = [
#     "Your satisfaction is my top priority. If there's anything else I can assist you with, please don't hesitate to let me know.",
#     "I'm at your service for any additional assistance you may require feel free to ask.",
# ]

# messages = []

# SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'User')}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]

# # ==================== CONTACT DATABASE ====================
# def load_contacts():
#     """Load saved contacts from file"""
#     try:
#         with open(r"Data/contacts.json", "r", encoding="utf-8") as f:
#             return json.load(f)
#     except (FileNotFoundError, json.JSONDecodeError):
#         default_contacts = {
#             "maa": "917749963694",
#             "papa": "1234567890",
#             "brother": "1234567891",
#             "sister": "1234567892"
#         }
#         os.makedirs("Data", exist_ok=True)
#         with open(r"Data/contacts.json", "w", encoding="utf-8") as f:
#             json.dump(default_contacts, f, indent=4)
#         return default_contacts

# def get_phone_number(contact_name):
#     """Get phone number from contact name"""
#     contacts = load_contacts()
#     contact_name = contact_name.lower().strip()
    
#     if contact_name in contacts:
#         return contacts[contact_name]
    
#     for name, number in contacts.items():
#         if contact_name in name or name in contact_name:
#             return number
    
#     return None

# # ==================== PRECISE VOLUME CONTROL ====================
# def set_volume(level):
#     """Set volume to exact percentage using Windows audio control"""
#     try:
#         # First try the precise method with pycaw
#         from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
#         from ctypes import cast, POINTER
#         from comtypes import CLSCTX_ALL
        
#         devices = AudioUtilities.GetSpeakers()
#         interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
#         volume = cast(interface, POINTER(IAudioEndpointVolume))
        
#         # Convert percentage to scalar (0.0 to 1.0)
#         scalar = max(0.0, min(1.0, level / 100.0))
#         volume.SetMasterVolumeLevelScalar(scalar, None)
        
#         return f"Volume set to {level}%"
        
#     except ImportError:
#         # Fallback if pycaw not installed
#         try:
#             if level == 0:
#                 for _ in range(2):
#                     keyboard.press_and_release("volume mute")
#                 return "Volume muted"
#             else:
#                 # First ensure not muted
#                 for _ in range(2):
#                     keyboard.press_and_release("volume mute")
                
#                 # For fallback, set to approximate level
#                 keyboard.press_and_release("volume up")
#                 return f"Volume adjusted (install pycaw for exact control)"
                
#         except Exception as e2:
#             return f"Volume control error: {str(e2)}"
        
#     except Exception as e:
#         return f"Error setting volume: {str(e)}"

# # ==================== IMPROVED MEDIA CONTROL ====================
# def MediaControl(action):
#     """Improved media control - NO auto-pausing, better resume functionality"""
#     try:
#         if action == "play" or action == "resume":
#             # Single press only - this will RESUME paused media
#             pyautogui.press('playpause')
#             return "Media resumed"
#         elif action == "pause":
#             # Single press only - this will PAUSE playing media
#             pyautogui.press('playpause')
#             return "Media paused"
#         elif action == "next":
#             pyautogui.press('nexttrack')
#             return "Next track"
#         elif action == "previous":
#             pyautogui.press('prevtrack')
#             return "Previous track"
#     except Exception as e:
#         return f"Error controlling media: {str(e)}"

# # ==================== MOBILE FUNCTIONS ====================
# def MobileOpenApp(app_name):
#     """Open app on mobile device"""
#     device_type = get_device_type()
#     connection = get_connection_method()
    
#     if device_type == "mobile" or connection == "adb":
#         try:
#             app_map = {
#                 "whatsapp": "com.whatsapp",
#                 "instagram": "com.instagram.android",
#                 "facebook": "com.facebook.katana",
#                 "chrome": "com.android.chrome",
#                 "youtube": "com.google.android.youtube",
#                 "spotify": "com.spotify.music",
#                 "music": "com.android.music",
#                 "messages": "com.android.mms",
#                 "phone": "com.android.dialer",
#                 "youtube music": "com.google.android.apps.youtube.music"
#             }
            
#             app_package = app_map.get(app_name.lower(), f"com.{app_name}")
            
#             if connection == "adb":
#                 result = subprocess.run(['adb', 'shell', 'am', 'start', '-n', f'{app_package}/.MainActivity'], 
#                                       capture_output=True, text=True, timeout=10)
#             else:
#                 result = subprocess.run(['am', 'start', '-n', f'{app_package}/.MainActivity'], 
#                                       capture_output=True, text=True, timeout=10)
            
#             if result.returncode == 0:
#                 return f"Opened {app_name} on mobile"
#             else:
#                 return f"Failed to open {app_name}"
                
#         except Exception as e:
#             return f"Error opening {app_name}: {str(e)}"
    
#     return "Mobile function called on non-mobile device"

# def MobileCall(contact):
#     """Make call on mobile"""
#     phone_number = get_phone_number(contact)
#     if not phone_number:
#         return f"Could not find number for {contact}"
    
#     device_type = get_device_type()
#     connection = get_connection_method()
    
#     if device_type == "mobile" or connection == "adb":
#         try:
#             if connection == "adb":
#                 result = subprocess.run(['adb', 'shell', 'am', 'start', '-a', 'android.intent.action.CALL', '-d', f'tel:{phone_number}'], 
#                                       capture_output=True, text=True, timeout=10)
#             else:
#                 result = subprocess.run(['am', 'start', '-a', 'android.intent.action.CALL', '-d', f'tel:{phone_number}'], 
#                                       capture_output=True, text=True, timeout=10)
            
#             if result.returncode == 0:
#                 return f"Calling {contact}"
#             else:
#                 return f"Call failed to initiate"
                
#         except Exception as e:
#             return f"Call error: {str(e)}"
    
#     return "Mobile function called on non-mobile device"

# def MobileSendMessage(contact, message_text=""):
#     """Send message on mobile"""
#     phone_number = get_phone_number(contact)
#     if not phone_number:
#         return f"Could not find number for {contact}"
    
#     device_type = get_device_type()
#     connection = get_connection_method()
    
#     if device_type == "mobile" or connection == "adb":
#         try:
#             if connection == "adb":
#                 result = subprocess.run(['adb', 'shell', 'am', 'start', '-a', 'android.intent.action.SENDTO', '-d', f'sms:{phone_number}', '--es', 'sms_body', message_text], 
#                                       capture_output=True, text=True, timeout=15)
#             else:
#                 result = subprocess.run(['am', 'start', '-a', 'android.intent.action.SENDTO', '-d', f'sms:{phone_number}', '--es', 'sms_body', message_text], 
#                                       capture_output=True, text=True, timeout=15)
            
#             if result.returncode == 0:
#                 return f"Message ready to send to {contact}"
#             else:
#                 return f"Message setup failed"
                
#         except Exception as e:
#             return f"Message error: {str(e)}"
    
#     return "Mobile function called on non-mobile device"

# def MobilePlayMusic(song_name=""):
#     """Mobile music control"""
#     try:
#         if not song_name or "music" in song_name.lower():
#             subprocess.run(['input', 'keyevent', '85'], timeout=5)
#             return "Resuming music playback"
        
#         music_apps = [
#             'com.spotify.music',
#             'com.google.android.apps.youtube.music',
#             'com.gaana',
#             'com.jio.media.jiobeats',
#             'com.apple.android.music'
#         ]
        
#         for app in music_apps:
#             try:
#                 result = subprocess.run(['am', 'start', '-n', f'{app}/.MainActivity'], 
#                                       timeout=10, capture_output=True)
#                 if result.returncode == 0:
#                     time.sleep(3)
#                     return f"Opened music app. Please play {song_name}"
#             except:
#                 continue
                
#         return "Could not open music app. Please play manually"
        
#     except Exception as e:
#         return f"Mobile music error: {str(e)}"

# # ==================== YOUTUBE FUNCTION ====================
# def PlayYoutube(query):
#     """Simple YouTube playback without auto-pausing"""
#     try:
#         playonyt(query)
#         return f"Playing {query} on YouTube"
#     except Exception as e:
#         return f"Error playing YouTube: {str(e)}"

# # ==================== IMPROVED MUSIC FUNCTION ====================
# def PlayMusic(song_name=""):
#     """Play music on YouTube Music - NO AUTO-PAUSING"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return MobileOpenApp("youtube music")
    
#     try:
#         song_name = song_name.replace("on music", "").replace("music", "").replace("on youtube music", "").strip()
        
#         if not song_name or "random" in song_name.lower():
#             # Open YouTube Music with a popular Bollywood playlist
#             webopen("https://music.youtube.com/watch?v=4hzr6qLFTzI&list=RDAMVM4hzr6qLFTzI")
#             time.sleep(8)  # Wait for page to load completely
            
#             # NO key presses after opening - let it play naturally
#             return "Playing Bollywood music on YouTube Music"
#         else:
#             # Search for the specific song on YouTube Music
#             search_query = f"{song_name} site:music.youtube.com"
#             search(search_query)
#             time.sleep(5)
#             return f"Searching for {song_name} on YouTube Music"
            
#     except Exception as e:
#         return f"Error playing music: {str(e)}"

# def PlaySpotify(song_name=""):
#     """Spotify control"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return MobileOpenApp("spotify")
    
#     try:
#         song_name = song_name.replace("on spotify", "").replace("spotify", "").strip().lower()
        
#         if not song_name or "music" in song_name.lower():
#             webopen("https://open.spotify.com")
#             time.sleep(5)
#             pyautogui.press('space')
#             return "Playing music on Spotify"
#         else:
#             return PlayYoutube(song_name)
            
#     except Exception as e:
#         return f"Error controlling Spotify: {str(e)}"

# # ==================== BASIC FUNCTIONS ====================
# def GoogleSearch(Topic):
#     """Perform a Google search"""
#     search(Topic)
#     return f"Searched Google for: {Topic}"

# def YouTubeSearch(Topic):
#     """Search on YouTube"""
#     Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
#     webbrowser.open(Url4Search)
#     return f"Searched YouTube for: {Topic}"

# def Content(Topic):
#     """Generate and open content in Notepad"""
    
#     def OpenNotepad(File):
#         default_text_editor = "notepad.exe"
#         subprocess.Popen([default_text_editor, File])
        
#     def ContentWriterAI(prompt):
#         if not client:
#             return "Groq API not configured"
            
#         messages.append({"role": "user", "content": f"{prompt}."})
        
#         completion = client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=SystemChatBot + messages,
#             temperature=0.7,
#             max_tokens=2048,
#             top_p=1,
#             stream=True,
#             stop=None
#         )
        
#         Answer = ""
#         for chunk in completion:
#             if chunk.choices[0].delta.content:
#                 Answer += chunk.choices[0].delta.content
                
#         Answer = Answer.replace("</s>", "")
#         messages.append({"role": "assistant", "content": Answer})
#         return Answer
    
#     Topic = Topic.replace("Content ", "")
#     ContentByAI = ContentWriterAI(Topic)
    
#     os.makedirs("Data", exist_ok=True)
#     filename = f"Data/{Topic.lower().replace(' ', '')}.txt"
#     with open(filename, "w", encoding="utf-8") as file:
#         file.write(ContentByAI)
    
#     OpenNotepad(filename)
#     return f"Created content: {Topic}"

# # ==================== APP OPENING FUNCTION ====================
# def OpenApp(app_name, sess=requests.session()):
#     """Open application or website"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return MobileOpenApp(app_name)
        
#     app_name = app_name.lower().strip()
#     print(f"OPENING {app_name.upper()}")
    
#     if "youtube music" in app_name or "yt music" in app_name:
#         webopen("https://music.youtube.com")
#         print("Opening YouTube Music")
#         return "Opened YouTube Music"
    
#     try:
#         result = appopen(app_name, throw_error=True, match_closest=True)
#         if result:
#             return f"Opened {app_name}"
#     except Exception as e:
#         print(f"App not found locally: {e}")
    
#     website_map = {
#         "whatsapp": "https://web.whatsapp.com",
#         "instagram": "https://www.instagram.com",
#         "facebook": "https://www.facebook.com",
#         "telegram": "https://web.telegram.org",
#         "spotify": "https://open.spotify.com",
#         "netflix": "https://www.netflix.com",
#         "twitter": "https://twitter.com",
#         "linkedin": "https://www.linkedin.com",
#         "youtube": "https://www.youtube.com",
#         "gmail": "https://mail.google.com",
#         "chrome": "https://www.google.com",
#         "discord": "https://discord.com/app",
#         "youtube music": "https://music.youtube.com",
#         "yt music": "https://music.youtube.com"
#     }
    
#     if app_name in website_map:
#         webopen(website_map[app_name])
#         print(f"Opening {app_name.upper()} official website")
#         return f"Opened {app_name}"
    
#     return f"Could not open {app_name}"

# # ==================== CLOSE APP FUNCTION ====================
# def CloseApp(app_name):
#     """Close application safely"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return "Close app not supported on mobile"
    
#     protected_apps = ["python", "vscode", "pycharm", "cmd", "terminal", "assistant", "zyra", "main"]
    
#     if any(protected in app_name.lower() for protected in protected_apps):
#         return f"Cannot close {app_name} - protected application"
    
#     print(f"CLOSING {app_name.upper()}")
    
#     try:
#         if any(browser in app_name.lower() for browser in ["chrome", "youtube", "spotify", "web", "browser"]):
#             pyautogui.hotkey('ctrl', 'w')
#             time.sleep(1)
#             return f"Closed {app_name} tab"
#         else:
#             result = subprocess.run(['taskkill', '/f', '/im', f'{app_name}.exe'], 
#                                   capture_output=True, text=True, timeout=10)
#             if result.returncode == 0:
#                 return f"Closed {app_name}"
#             else:
#                 return f"Could not close {app_name}"
                
#     except Exception as e:
#         return f"Error closing {app_name}: {str(e)}"

# # ==================== FIXED SYSTEM CONTROL ====================
# def System(command):
#     """Fixed system control with proper mute handling"""
#     device_type = get_device_type()
#     if device_type == "mobile":
#         return "System commands not supported on mobile"
    
#     command = command.strip().lower()
    
#     # Handle media controls - "play" now means "resume"
#     if command in ["play", "resume", "pause", "next", "previous"]:
#         return MediaControl(command)
    
#     # Handle mute/unmute specifically
#     if command == "mute":
#         return set_volume(0)
#     elif command == "unmute":
#         return set_volume(50)  # Set to 50% when unmuting
    
#     # Handle volume commands with exact percentages
#     if any(word in command for word in ["volume", "vol"]):
#         numbers = [int(s) for s in command.split() if s.isdigit()]
        
#         if numbers:
#             level = min(max(numbers[0], 0), 100)
#             return set_volume(level)
#         elif "full" in command or "max" in command or "100" in command:
#             return set_volume(100)
#         elif "up" in command:
#             return "Use specific volume level like 'volume 50'"
#         elif "down" in command:
#             return "Use specific volume level like 'volume 30'"
    
#     # Other system commands
#     if command == "lock":
#         try:
#             subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
#             return "PC locked"
#         except Exception as e:
#             return f"Error locking PC: {e}"
            
#     elif command == "shutdown":
#         os.system("shutdown /s /t 10")
#         return "Shutting down computer in 10 seconds..."
            
#     elif command == "restart":
#         os.system("shutdown /r /t 1")
#         return "Restarting computer..."
    
#     return f"Unknown system command: {command}"

# # ==================== WHATSAPP FUNCTION ====================
# def SendMessage(contact, message_text=""):
#     """WhatsApp messaging"""
#     device_type = get_device_type()
#     if device_type == "mobile":
#         return MobileSendMessage(contact, message_text)
    
#     print(f"[MESSAGE] Sending to {contact}: {message_text}")
    
#     try:
#         phone_number = get_phone_number(contact)
#         if not phone_number:
#             phone_number = ''.join(filter(str.isdigit, contact))
        
#         if not phone_number:
#             webopen("https://web.whatsapp.com")
#             return f"Opened WhatsApp. Please search for '{contact}' and send: '{message_text}'"
        
#         phone_number = ''.join(filter(str.isdigit, phone_number))
#         if len(phone_number) == 10:
#             phone_number = '91' + phone_number
        
#         encoded_message = requests.utils.quote(message_text)
#         whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_message}"
        
#         webopen(whatsapp_url)
#         time.sleep(4)
#         pyautogui.press('enter')
#         time.sleep(2)
        
#         pyautogui.hotkey('ctrl', 'w')
        
#         return f"Message sent to {contact}"
        
#     except Exception as e:
#         return f"Error: {str(e)}. Please message manually."

# # ==================== CALLING FUNCTION ====================
# def CallContact(contact):
#     """Calling implementation"""
#     device_type = get_device_type()
#     if device_type == "mobile":
#         return MobileCall(contact)
    
#     print(f"[CALL] Calling: {contact}")
    
#     try:
#         phone_number = get_phone_number(contact)
#         if not phone_number:
#             phone_number = ''.join(filter(str.isdigit, contact))
        
#         if not phone_number:
#             return f"Could not find phone number for {contact}"
        
#         if len(phone_number) == 10:
#             phone_number = '91' + phone_number
        
#         webopen(f"tel:{phone_number}")
#         return f"Calling {contact} ({phone_number})"
        
#     except Exception as e:
#         return f"Error initiating call: {str(e)}"

# # ==================== COMMAND EXECUTION ====================
# async def ExecuteCommand(command):
#     """Execute a single command and return result"""
#     print(f"[AUTOMATION] Processing command: {command}")
    
#     if command in ["play", "resume", "pause", "next", "previous"]:
#         return MediaControl(command)
    
#     if command.startswith("open "):
#         app_name = command.removeprefix("open ").strip()
#         return OpenApp(app_name)
            
#     elif command.startswith("close "):
#         app_name = command.removeprefix("close ").strip()
#         return CloseApp(app_name)
        
#     elif command.startswith("play "):
#         song_name = command.removeprefix("play ").strip()
        
#         if "on spotify" in song_name.lower():
#             song_name = song_name.replace("on spotify", "").strip()
#             return PlaySpotify(song_name)
#         elif "on youtube music" in song_name.lower():
#             song_name = song_name.replace("on youtube music", "").strip()
#             return PlayMusic(song_name)
#         elif "on youtube" in song_name.lower():
#             song_name = song_name.replace("on youtube", "").strip()
#             return PlayYoutube(song_name)
#         elif "on music" in song_name.lower():
#             song_name = song_name.replace("on music", "").strip()
#             return PlayMusic(song_name)
#         elif "music" in song_name.lower() or not song_name:
#             return PlayMusic(song_name)
#         else:
#             return PlayYoutube(song_name)
        
#     elif command.startswith("content "):
#         return Content(command.removeprefix("content "))
        
#     elif command.startswith("google search "):
#         return GoogleSearch(command.removeprefix("google search "))
        
#     elif command.startswith("youtube search "):
#         return YouTubeSearch(command.removeprefix("youtube search "))
        
#     elif command.startswith("system "):
#         sys_command = command.removeprefix("system ")
#         sys_command = sys_command.replace("_", " ").strip()
#         return System(sys_command)
        
#     elif command.startswith("call "):
#         contact = command.removeprefix("call ")
#         return CallContact(contact)
        
#     elif command.startswith("message "):
#         parts = command.removeprefix("message ").split(" ", 1)
#         contact = parts[0]
#         message_text = parts[1] if len(parts) > 1 else ""
#         return SendMessage(contact, message_text)
        
#     elif command == "exit":
#         return "Exiting assistant"
        
#     else:
#         return f"No function found for: {command}"

# async def Automation(commands: list[str]):
#     """Main automation function - execute all commands and return results"""
#     results = []
    
#     for command in commands:
#         try:
#             result = await ExecuteCommand(command)
#             results.append(result)
#             print(f"[RESULT] {result}")
#         except Exception as e:
#             error_msg = f"Error executing '{command}': {str(e)}"
#             results.append(error_msg)
#             print(f"[ERROR] {error_msg}")
    
#     return results
        
# if __name__ == "__main__":
#     print("=== Automation.py Test Mode ===")
#     print("This file is meant to be imported, not run directly.")
#     print("To test, run your main application that calls the Automation() function.")


# ===============================================Used code ended=================================================








# import cohere
# from AppOpener import close, open as appopen
# from webbrowser import open as webopen
# from pywhatkit import search, playonyt
# from dotenv import dotenv_values
# from bs4 import BeautifulSoup
# from rich import print
# from groq import Groq
# import webbrowser
# import subprocess
# import requests
# import keyboard
# import asyncio
# import os
# import contextlib
# import sys
# import io
# import pyautogui
# import time
# import json
# import random

# # Import device manager
# try:
#     from Backend.device_manager import get_device_type, get_connection_method
# except ImportError:
#     # Fallback if device_manager not found
#     def get_device_type():
#         return "pc"
#     def get_connection_method():
#         return "none"

# env_vars = dotenv_values(".env")
# GroqAPIKey = env_vars.get("GroqAPIKey")
# CohereAPIKey = env_vars.get("CohereAPIKey")

# co = cohere.Client(api_key=CohereAPIKey) if CohereAPIKey else None

# classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "O5uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table__webanswers-table", "dDoNo ikb48b gsrt", "sXLaOe", "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

# useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None

# professional_responses = [
#     "Your satisfaction is my top priority. If there's anything else I can assist you with, please don't hesitate to let me know.",
#     "I'm at your service for any additional assistance you may require feel free to ask.",
# ]

# messages = []

# SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'User')}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]

# # ==================== CONTACT DATABASE ====================
# def load_contacts():
#     """Load saved contacts from file"""
#     try:
#         with open(r"Data/contacts.json", "r", encoding="utf-8") as f:
#             return json.load(f)
#     except (FileNotFoundError, json.JSONDecodeError):
#         default_contacts = {
#             "maa": "917749963694",
#             "papa": "1234567890",
#             "brother": "1234567891",
#             "sister": "1234567892"
#         }
#         os.makedirs("Data", exist_ok=True)
#         with open(r"Data/contacts.json", "w", encoding="utf-8") as f:
#             json.dump(default_contacts, f, indent=4)
#         return default_contacts

# def get_phone_number(contact_name):
#     """Get phone number from contact name"""
#     contacts = load_contacts()
#     contact_name = contact_name.lower().strip()
    
#     if contact_name in contacts:
#         return contacts[contact_name]
    
#     for name, number in contacts.items():
#         if contact_name in name or name in contact_name:
#             return number
    
#     return None

# # ==================== PRECISE VOLUME CONTROL ====================
# def set_volume(level):
#     """Set volume to exact percentage using Windows audio control"""
#     try:
#         # First try the precise method with pycaw
#         from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
#         from ctypes import cast, POINTER
#         from comtypes import CLSCTX_ALL
        
#         devices = AudioUtilities.GetSpeakers()
#         interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
#         volume = cast(interface, POINTER(IAudioEndpointVolume))
        
#         # Convert percentage to scalar (0.0 to 1.0)
#         scalar = max(0.0, min(1.0, level / 100.0))
#         volume.SetMasterVolumeLevelScalar(scalar, None)
        
#         return f"Volume set to {level}%"
        
#     except ImportError:
#         # Fallback if pycaw not installed
#         try:
#             if level == 0:
#                 for _ in range(2):
#                     keyboard.press_and_release("volume mute")
#                 return "Volume muted"
#             else:
#                 # First ensure not muted
#                 for _ in range(2):
#                     keyboard.press_and_release("volume mute")
                
#                 # For fallback, set to approximate level
#                 keyboard.press_and_release("volume up")
#                 return f"Volume adjusted (install pycaw for exact control)"
                
#         except Exception as e2:
#             return f"Volume control error: {str(e2)}"
        
#     except Exception as e:
#         return f"Error setting volume: {str(e)}"

# # ==================== IMPROVED MEDIA CONTROL ====================
# def MediaControl(action):
#     """Improved media control - NO auto-pausing, better resume functionality"""
#     try:
#         if action == "play" or action == "resume":
#             # Single press only - this will RESUME paused media
#             pyautogui.press('playpause')
#             return "Media resumed"
#         elif action == "pause":
#             # Single press only - this will PAUSE playing media
#             pyautogui.press('playpause')
#             return "Media paused"
#         elif action == "next":
#             pyautogui.press('nexttrack')
#             return "Next track"
#         elif action == "previous":
#             pyautogui.press('prevtrack')
#             return "Previous track"
#     except Exception as e:
#         return f"Error controlling media: {str(e)}"

# # ==================== MOBILE FUNCTIONS ====================
# def MobileOpenApp(app_name):
#     """Open app on mobile device"""
#     device_type = get_device_type()
#     connection = get_connection_method()
    
#     if device_type == "mobile" or connection == "adb":
#         try:
#             app_map = {
#                 "whatsapp": "com.whatsapp",
#                 "instagram": "com.instagram.android",
#                 "facebook": "com.facebook.katana",
#                 "chrome": "com.android.chrome",
#                 "youtube": "com.google.android.youtube",
#                 "spotify": "com.spotify.music",
#                 "music": "com.android.music",
#                 "messages": "com.android.mms",
#                 "phone": "com.android.dialer",
#                 "youtube music": "com.google.android.apps.youtube.music"
#             }
            
#             app_package = app_map.get(app_name.lower(), f"com.{app_name}")
            
#             if connection == "adb":
#                 result = subprocess.run(['adb', 'shell', 'am', 'start', '-n', f'{app_package}/.MainActivity'], 
#                                       capture_output=True, text=True, timeout=10)
#             else:
#                 result = subprocess.run(['am', 'start', '-n', f'{app_package}/.MainActivity'], 
#                                       capture_output=True, text=True, timeout=10)
            
#             if result.returncode == 0:
#                 return f"Opened {app_name} on mobile"
#             else:
#                 return f"Failed to open {app_name}"
                
#         except Exception as e:
#             return f"Error opening {app_name}: {str(e)}"
    
#     return "Mobile function called on non-mobile device"

# def MobileCall(contact):
#     """Make call on mobile"""
#     phone_number = get_phone_number(contact)
#     if not phone_number:
#         return f"Could not find number for {contact}"
    
#     device_type = get_device_type()
#     connection = get_connection_method()
    
#     if device_type == "mobile" or connection == "adb":
#         try:
#             if connection == "adb":
#                 result = subprocess.run(['adb', 'shell', 'am', 'start', '-a', 'android.intent.action.CALL', '-d', f'tel:{phone_number}'], 
#                                       capture_output=True, text=True, timeout=10)
#             else:
#                 result = subprocess.run(['am', 'start', '-a', 'android.intent.action.CALL', '-d', f'tel:{phone_number}'], 
#                                       capture_output=True, text=True, timeout=10)
            
#             if result.returncode == 0:
#                 return f"Calling {contact}"
#             else:
#                 return f"Call failed to initiate"
                
#         except Exception as e:
#             return f"Call error: {str(e)}"
    
#     return "Mobile function called on non-mobile device"

# def MobileSendMessage(contact, message_text=""):
#     """Send message on mobile"""
#     phone_number = get_phone_number(contact)
#     if not phone_number:
#         return f"Could not find number for {contact}"
    
#     device_type = get_device_type()
#     connection = get_connection_method()
    
#     if device_type == "mobile" or connection == "adb":
#         try:
#             if connection == "adb":
#                 result = subprocess.run(['adb', 'shell', 'am', 'start', '-a', 'android.intent.action.SENDTO', '-d', f'sms:{phone_number}', '--es', 'sms_body', message_text], 
#                                       capture_output=True, text=True, timeout=15)
#             else:
#                 result = subprocess.run(['am', 'start', '-a', 'android.intent.action.SENDTO', '-d', f'sms:{phone_number}', '--es', 'sms_body', message_text], 
#                                       capture_output=True, text=True, timeout=15)
            
#             if result.returncode == 0:
#                 return f"Message ready to send to {contact}"
#             else:
#                 return f"Message setup failed"
                
#         except Exception as e:
#             return f"Message error: {str(e)}"
    
#     return "Mobile function called on non-mobile device"

# def MobilePlayMusic(song_name=""):
#     """Mobile music control"""
#     try:
#         if not song_name or "music" in song_name.lower():
#             subprocess.run(['input', 'keyevent', '85'], timeout=5)
#             return "Resuming music playback"
        
#         music_apps = [
#             'com.spotify.music',
#             'com.google.android.apps.youtube.music',
#             'com.gaana',
#             'com.jio.media.jiobeats',
#             'com.apple.android.music'
#         ]
        
#         for app in music_apps:
#             try:
#                 result = subprocess.run(['am', 'start', '-n', f'{app}/.MainActivity'], 
#                                       timeout=10, capture_output=True)
#                 if result.returncode == 0:
#                     time.sleep(3)
#                     return f"Opened music app. Please play {song_name}"
#             except:
#                 continue
                
#         return "Could not open music app. Please play manually"
        
#     except Exception as e:
#         return f"Mobile music error: {str(e)}"

# # ==================== YOUTUBE FUNCTION ====================
# def PlayYoutube(query):
#     """Simple YouTube playback without auto-pausing"""
#     try:
#         playonyt(query)
#         return f"Playing {query} on YouTube"
#     except Exception as e:
#         return f"Error playing YouTube: {str(e)}"

# # ==================== IMPROVED MUSIC FUNCTION ====================
# def PlayMusic(song_name=""):
#     """Play music on YouTube Music - NO AUTO-PAUSING"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return MobileOpenApp("youtube music")
    
#     try:
#         song_name = song_name.replace("on music", "").replace("music", "").replace("on youtube music", "").strip()
        
#         if not song_name or "random" in song_name.lower():
#             # Open YouTube Music with a popular Bollywood playlist
#             webopen("https://music.youtube.com/watch?v=4hzr6qLFTzI&list=RDAMVM4hzr6qLFTzI")
#             time.sleep(8)  # Wait for page to load completely
            
#             # NO key presses after opening - let it play naturally
#             return "Playing Bollywood music on YouTube Music"
#         else:
#             # Search for the specific song on YouTube Music
#             search_query = f"{song_name} site:music.youtube.com"
#             search(search_query)
#             time.sleep(5)
#             return f"Searching for {song_name} on YouTube Music"
            
#     except Exception as e:
#         return f"Error playing music: {str(e)}"

# def PlaySpotify(song_name=""):
#     """Spotify control"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return MobileOpenApp("spotify")
    
#     try:
#         song_name = song_name.replace("on spotify", "").replace("spotify", "").strip().lower()
        
#         if not song_name or "music" in song_name.lower():
#             webopen("https://open.spotify.com")
#             time.sleep(5)
#             pyautogui.press('space')
#             return "Playing music on Spotify"
#         else:
#             return PlayYoutube(song_name)
            
#     except Exception as e:
#         return f"Error controlling Spotify: {str(e)}"

# # ==================== BASIC FUNCTIONS ====================
# def GoogleSearch(Topic):
#     """Perform a Google search"""
#     search(Topic)
#     return f"Searched Google for: {Topic}"

# def YouTubeSearch(Topic):
#     """Search on YouTube"""
#     Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
#     webbrowser.open(Url4Search)
#     return f"Searched YouTube for: {Topic}"

# def Content(Topic):
#     """Generate and open content in Notepad"""
    
#     def OpenNotepad(File):
#         default_text_editor = "notepad.exe"
#         subprocess.Popen([default_text_editor, File])
        
#     def ContentWriterAI(prompt):
#         if not client:
#             return "Groq API not configured"
            
#         messages.append({"role": "user", "content": f"{prompt}."})
        
#         completion = client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=SystemChatBot + messages,
#             temperature=0.7,
#             max_tokens=2048,
#             top_p=1,
#             stream=True,
#             stop=None
#         )
        
#         Answer = ""
#         for chunk in completion:
#             if chunk.choices[0].delta.content:
#                 Answer += chunk.choices[0].delta.content
                
#         Answer = Answer.replace("</s>", "")
#         messages.append({"role": "assistant", "content": Answer})
#         return Answer
    
#     Topic = Topic.replace("Content ", "")
#     ContentByAI = ContentWriterAI(Topic)
    
#     os.makedirs("Data", exist_ok=True)
#     filename = f"Data/{Topic.lower().replace(' ', '')}.txt"
#     with open(filename, "w", encoding="utf-8") as file:
#         file.write(ContentByAI)
    
#     OpenNotepad(filename)
#     return f"Created content: {Topic}"

# # ==================== APP OPENING FUNCTION ====================
# def OpenApp(app_name, sess=requests.session()):
#     """Open application or website"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return MobileOpenApp(app_name)
        
#     app_name = app_name.lower().strip()
#     print(f"OPENING {app_name.upper()}")
    
#     if "youtube music" in app_name or "yt music" in app_name:
#         webopen("https://music.youtube.com")
#         print("Opening YouTube Music")
#         return "Opened YouTube Music"
    
#     try:
#         result = appopen(app_name, throw_error=True, match_closest=True)
#         if result:
#             return f"Opened {app_name}"
#     except Exception as e:
#         print(f"App not found locally: {e}")
    
#     website_map = {
#         "whatsapp": "https://web.whatsapp.com",
#         "instagram": "https://www.instagram.com",
#         "facebook": "https://www.facebook.com",
#         "telegram": "https://web.telegram.org",
#         "spotify": "https://open.spotify.com",
#         "netflix": "https://www.netflix.com",
#         "twitter": "https://twitter.com",
#         "linkedin": "https://www.linkedin.com",
#         "youtube": "https://www.youtube.com",
#         "gmail": "https://mail.google.com",
#         "chrome": "https://www.google.com",
#         "discord": "https://discord.com/app",
#         "youtube music": "https://music.youtube.com",
#         "yt music": "https://music.youtube.com"
#     }
    
#     if app_name in website_map:
#         webopen(website_map[app_name])
#         print(f"Opening {app_name.upper()} official website")
#         return f"Opened {app_name}"
    
#     return f"Could not open {app_name}"

# # ==================== CLOSE APP FUNCTION ====================
# def CloseApp(app_name):
#     """Close application safely"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return "Close app not supported on mobile"
    
#     protected_apps = ["python", "vscode", "pycharm", "cmd", "terminal", "assistant", "zyra", "main"]
    
#     if any(protected in app_name.lower() for protected in protected_apps):
#         return f"Cannot close {app_name} - protected application"
    
#     print(f"CLOSING {app_name.upper()}")
    
#     try:
#         if any(browser in app_name.lower() for browser in ["chrome", "youtube", "spotify", "web", "browser"]):
#             pyautogui.hotkey('ctrl', 'w')
#             time.sleep(1)
#             return f"Closed {app_name} tab"
#         else:
#             result = subprocess.run(['taskkill', '/f', '/im', f'{app_name}.exe'], 
#                                   capture_output=True, text=True, timeout=10)
#             if result.returncode == 0:
#                 return f"Closed {app_name}"
#             else:
#                 return f"Could not close {app_name}"
                
#     except Exception as e:
#         return f"Error closing {app_name}: {str(e)}"

# # ==================== FIXED SYSTEM CONTROL ====================
# def System(command):
#     """Fixed system control with proper mute handling"""
#     device_type = get_device_type()
#     if device_type == "mobile":
#         return "System commands not supported on mobile"
    
#     command = command.strip().lower()
    
#     # Handle media controls - "play" now means "resume"
#     if command in ["play", "resume", "pause", "next", "previous"]:
#         return MediaControl(command)
    
#     # Handle mute/unmute specifically
#     if command == "mute":
#         return set_volume(0)
#     elif command == "unmute":
#         return set_volume(50)  # Set to 50% when unmuting
    
#     # Handle volume commands with exact percentages
#     if any(word in command for word in ["volume", "vol"]):
#         numbers = [int(s) for s in command.split() if s.isdigit()]
        
#         if numbers:
#             level = min(max(numbers[0], 0), 100)
#             return set_volume(level)
#         elif "full" in command or "max" in command or "100" in command:
#             return set_volume(100)
#         elif "up" in command:
#             return "Use specific volume level like 'volume 50'"
#         elif "down" in command:
#             return "Use specific volume level like 'volume 30'"
    
#     # Other system commands
#     if command == "lock":
#         try:
#             subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
#             return "PC locked"
#         except Exception as e:
#             return f"Error locking PC: {e}"
            
#     elif command == "shutdown":
#         os.system("shutdown /s /t 10")
#         return "Shutting down computer in 10 seconds..."
            
#     elif command == "restart":
#         os.system("shutdown /r /t 1")
#         return "Restarting computer..."
    
#     return f"Unknown system command: {command}"

# # ==================== WHATSAPP FUNCTION ====================
# def SendMessage(contact, message_text=""):
#     """WhatsApp messaging"""
#     device_type = get_device_type()
#     if device_type == "mobile":
#         return MobileSendMessage(contact, message_text)
    
#     print(f"[MESSAGE] Sending to {contact}: {message_text}")
    
#     try:
#         phone_number = get_phone_number(contact)
#         if not phone_number:
#             phone_number = ''.join(filter(str.isdigit, contact))
        
#         if not phone_number:
#             webopen("https://web.whatsapp.com")
#             return f"Opened WhatsApp. Please search for '{contact}' and send: '{message_text}'"
        
#         phone_number = ''.join(filter(str.isdigit, phone_number))
#         if len(phone_number) == 10:
#             phone_number = '91' + phone_number
        
#         encoded_message = requests.utils.quote(message_text)
#         whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_message}"
        
#         webopen(whatsapp_url)
#         time.sleep(4)
#         pyautogui.press('enter')
#         time.sleep(2)
        
#         pyautogui.hotkey('ctrl', 'w')
        
#         return f"Message sent to {contact}"
        
#     except Exception as e:
#         return f"Error: {str(e)}. Please message manually."

# # ==================== CALLING FUNCTION ====================
# def CallContact(contact):
#     """Calling implementation"""
#     device_type = get_device_type()
#     if device_type == "mobile":
#         return MobileCall(contact)
    
#     print(f"[CALL] Calling: {contact}")
    
#     try:
#         phone_number = get_phone_number(contact)
#         if not phone_number:
#             phone_number = ''.join(filter(str.isdigit, contact))
        
#         if not phone_number:
#             return f"Could not find phone number for {contact}"
        
#         if len(phone_number) == 10:
#             phone_number = '91' + phone_number
        
#         webopen(f"tel:{phone_number}")
#         return f"Calling {contact} ({phone_number})"
        
#     except Exception as e:
#         return f"Error initiating call: {str(e)}"

# # ==================== COMMAND EXECUTION ====================
# async def ExecuteCommand(command):
#     """Execute a single command and return result"""
#     print(f"[AUTOMATION] Processing command: {command}")
    
#     if command in ["play", "resume", "pause", "next", "previous"]:
#         return MediaControl(command)
    
#     if command.startswith("open "):
#         app_name = command.removeprefix("open ").strip()
#         return OpenApp(app_name)
            
#     elif command.startswith("close "):
#         app_name = command.removeprefix("close ").strip()
#         return CloseApp(app_name)
        
#     elif command.startswith("play "):
#         song_name = command.removeprefix("play ").strip()
        
#         if "on spotify" in song_name.lower():
#             song_name = song_name.replace("on spotify", "").strip()
#             return PlaySpotify(song_name)
#         elif "on youtube music" in song_name.lower():
#             song_name = song_name.replace("on youtube music", "").strip()
#             return PlayMusic(song_name)
#         elif "on youtube" in song_name.lower():
#             song_name = song_name.replace("on youtube", "").strip()
#             return PlayYoutube(song_name)
#         elif "on music" in song_name.lower():
#             song_name = song_name.replace("on music", "").strip()
#             return PlayMusic(song_name)
#         elif "music" in song_name.lower() or not song_name:
#             return PlayMusic(song_name)
#         else:
#             return PlayYoutube(song_name)
        
#     elif command.startswith("content "):
#         return Content(command.removeprefix("content "))
        
#     elif command.startswith("google search "):
#         return GoogleSearch(command.removeprefix("google search "))
        
#     elif command.startswith("youtube search "):
#         return YouTubeSearch(command.removeprefix("youtube search "))
        
#     elif command.startswith("system "):
#         sys_command = command.removeprefix("system ")
#         sys_command = sys_command.replace("_", " ").strip()
#         return System(sys_command)
        
#     elif command.startswith("call "):
#         contact = command.removeprefix("call ")
#         return CallContact(contact)
        
#     elif command.startswith("message "):
#         parts = command.removeprefix("message ").split(" ", 1)
#         contact = parts[0]
#         message_text = parts[1] if len(parts) > 1 else ""
#         return SendMessage(contact, message_text)
        
#     elif command == "exit":
#         return "Exiting assistant"
        
#     else:
#         return f"No function found for: {command}"

# async def Automation(commands: list[str]):
#     """Main automation function - execute all commands and return results"""
#     results = []
    
#     for command in commands:
#         try:
#             result = await ExecuteCommand(command)
#             results.append(result)
#             print(f"[RESULT] {result}")
#         except Exception as e:
#             error_msg = f"Error executing '{command}': {str(e)}"
#             results.append(error_msg)
#             print(f"[ERROR] {error_msg}")
    
#     return results
        
# if __name__ == "__main__":
#     print("=== Automation.py Test Mode ===")
#     print("This file is meant to be imported, not run directly.")
#     print("To test, run your main application that calls the Automation() function.")


















# import cohere
# from AppOpener import close, open as appopen
# from webbrowser import open as webopen
# from pywhatkit import search, playonyt
# from dotenv import dotenv_values
# from bs4 import BeautifulSoup
# from rich import print
# from groq import Groq
# import webbrowser
# import subprocess
# import requests
# import keyboard
# import asyncio
# import os
# import contextlib
# import sys
# import io
# import pyautogui
# import time
# import json
# import random

# # Import device manager
# try:
#     from Backend.device_manager import get_device_type, get_connection_method
# except ImportError:
#     # Fallback if device_manager not found
#     def get_device_type():
#         return "pc"
#     def get_connection_method():
#         return "none"

# env_vars = dotenv_values(".env")
# GroqAPIKey = env_vars.get("GroqAPIKey")
# CohereAPIKey = env_vars.get("CohereAPIKey")

# co = cohere.Client(api_key=CohereAPIKey) if CohereAPIKey else None

# classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "O5uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table__webanswers-table", "dDoNo ikb48b gsrt", "sXLaOe", "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

# useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None

# professional_responses = [
#     "Your satisfaction is my top priority. If there's anything else I can assist you with, please don't hesitate to let me know.",
#     "I'm at your service for any additional assistance you may require feel free to ask.",
# ]

# messages = []

# SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'User')}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]

# # ==================== CONTACT DATABASE ====================
# def load_contacts():
#     """Load saved contacts from file"""
#     try:
#         with open(r"Data/contacts.json", "r", encoding="utf-8") as f:
#             return json.load(f)
#     except (FileNotFoundError, json.JSONDecodeError):
#         default_contacts = {
#             "maa": "917749963694",
#             "papa": "1234567890",
#             "brother": "1234567891",
#             "sister": "1234567892"
#         }
#         os.makedirs("Data", exist_ok=True)
#         with open(r"Data/contacts.json", "w", encoding="utf-8") as f:
#             json.dump(default_contacts, f, indent=4)
#         return default_contacts

# def get_phone_number(contact_name):
#     """Get phone number from contact name"""
#     contacts = load_contacts()
#     contact_name = contact_name.lower().strip()
    
#     if contact_name in contacts:
#         return contacts[contact_name]
    
#     for name, number in contacts.items():
#         if contact_name in name or name in contact_name:
#             return number
    
#     return None

# # ==================== PRECISE VOLUME CONTROL ====================
# def set_volume(level):
#     """Set volume to exact percentage using Windows audio control"""
#     try:
#         # First try the precise method with pycaw
#         from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
#         from ctypes import cast, POINTER
#         from comtypes import CLSCTX_ALL
        
#         devices = AudioUtilities.GetSpeakers()
#         interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
#         volume = cast(interface, POINTER(IAudioEndpointVolume))
        
#         # Convert percentage to scalar (0.0 to 1.0)
#         scalar = max(0.0, min(1.0, level / 100.0))
#         volume.SetMasterVolumeLevelScalar(scalar, None)
        
#         return f"Volume set to {level}%"
        
#     except ImportError:
#         # Fallback if pycaw not installed
#         try:
#             if level == 0:
#                 for _ in range(2):
#                     keyboard.press_and_release("volume mute")
#                 return "Volume muted"
#             else:
#                 # First ensure not muted
#                 for _ in range(2):
#                     keyboard.press_and_release("volume mute")
                
#                 # For fallback, set to approximate level
#                 keyboard.press_and_release("volume up")
#                 return f"Volume adjusted (install pycaw for exact control)"
                
#         except Exception as e2:
#             return f"Volume control error: {str(e2)}"
        
#     except Exception as e:
#         return f"Error setting volume: {str(e)}"

# # ==================== SIMPLE MEDIA CONTROL ====================
# def MediaControl(action):
#     """Simple media control without auto-pausing"""
#     try:
#         if action == "play":
#             pyautogui.press('playpause')  # Single press only
#             return "Media playing"
#         elif action == "pause":
#             pyautogui.press('playpause')  # Single press only
#             return "Media paused"
#         elif action == "next":
#             pyautogui.press('nexttrack')
#             return "Next track"
#         elif action == "previous":
#             pyautogui.press('prevtrack')
#             return "Previous track"
#     except Exception as e:
#         return f"Error controlling media: {str(e)}"

# # ==================== MOBILE FUNCTIONS ====================
# def MobileOpenApp(app_name):
#     """Open app on mobile device"""
#     device_type = get_device_type()
#     connection = get_connection_method()
    
#     if device_type == "mobile" or connection == "adb":
#         try:
#             app_map = {
#                 "whatsapp": "com.whatsapp",
#                 "instagram": "com.instagram.android",
#                 "facebook": "com.facebook.katana",
#                 "chrome": "com.android.chrome",
#                 "youtube": "com.google.android.youtube",
#                 "spotify": "com.spotify.music",
#                 "music": "com.android.music",
#                 "messages": "com.android.mms",
#                 "phone": "com.android.dialer",
#                 "youtube music": "com.google.android.apps.youtube.music"
#             }
            
#             app_package = app_map.get(app_name.lower(), f"com.{app_name}")
            
#             if connection == "adb":
#                 result = subprocess.run(['adb', 'shell', 'am', 'start', '-n', f'{app_package}/.MainActivity'], 
#                                       capture_output=True, text=True, timeout=10)
#             else:
#                 result = subprocess.run(['am', 'start', '-n', f'{app_package}/.MainActivity'], 
#                                       capture_output=True, text=True, timeout=10)
            
#             if result.returncode == 0:
#                 return f"Opened {app_name} on mobile"
#             else:
#                 return f"Failed to open {app_name}"
                
#         except Exception as e:
#             return f"Error opening {app_name}: {str(e)}"
    
#     return "Mobile function called on non-mobile device"

# def MobileCall(contact):
#     """Make call on mobile"""
#     phone_number = get_phone_number(contact)
#     if not phone_number:
#         return f"Could not find number for {contact}"
    
#     device_type = get_device_type()
#     connection = get_connection_method()
    
#     if device_type == "mobile" or connection == "adb":
#         try:
#             if connection == "adb":
#                 result = subprocess.run(['adb', 'shell', 'am', 'start', '-a', 'android.intent.action.CALL', '-d', f'tel:{phone_number}'], 
#                                       capture_output=True, text=True, timeout=10)
#             else:
#                 result = subprocess.run(['am', 'start', '-a', 'android.intent.action.CALL', '-d', f'tel:{phone_number}'], 
#                                       capture_output=True, text=True, timeout=10)
            
#             if result.returncode == 0:
#                 return f"Calling {contact}"
#             else:
#                 return f"Call failed to initiate"
                
#         except Exception as e:
#             return f"Call error: {str(e)}"
    
#     return "Mobile function called on non-mobile device"

# def MobileSendMessage(contact, message_text=""):
#     """Send message on mobile"""
#     phone_number = get_phone_number(contact)
#     if not phone_number:
#         return f"Could not find number for {contact}"
    
#     device_type = get_device_type()
#     connection = get_connection_method()
    
#     if device_type == "mobile" or connection == "adb":
#         try:
#             if connection == "adb":
#                 result = subprocess.run(['adb', 'shell', 'am', 'start', '-a', 'android.intent.action.SENDTO', '-d', f'sms:{phone_number}', '--es', 'sms_body', message_text], 
#                                       capture_output=True, text=True, timeout=15)
#             else:
#                 result = subprocess.run(['am', 'start', '-a', 'android.intent.action.SENDTO', '-d', f'sms:{phone_number}', '--es', 'sms_body', message_text], 
#                                       capture_output=True, text=True, timeout=15)
            
#             if result.returncode == 0:
#                 return f"Message ready to send to {contact}"
#             else:
#                 return f"Message setup failed"
                
#         except Exception as e:
#             return f"Message error: {str(e)}"
    
#     return "Mobile function called on non-mobile device"

# def MobilePlayMusic(song_name=""):
#     """Mobile music control"""
#     try:
#         if not song_name or "music" in song_name.lower():
#             subprocess.run(['input', 'keyevent', '85'], timeout=5)
#             return "Resuming music playback"
        
#         music_apps = [
#             'com.spotify.music',
#             'com.google.android.apps.youtube.music',
#             'com.gaana',
#             'com.jio.media.jiobeats',
#             'com.apple.android.music'
#         ]
        
#         for app in music_apps:
#             try:
#                 result = subprocess.run(['am', 'start', '-n', f'{app}/.MainActivity'], 
#                                       timeout=10, capture_output=True)
#                 if result.returncode == 0:
#                     time.sleep(3)
#                     return f"Opened music app. Please play {song_name}"
#             except:
#                 continue
                
#         return "Could not open music app. Please play manually"
        
#     except Exception as e:
#         return f"Mobile music error: {str(e)}"

# # ==================== YOUTUBE FUNCTION ====================
# def PlayYoutube(query):
#     """Simple YouTube playback without auto-pausing"""
#     try:
#         playonyt(query)
#         return f"Playing {query} on YouTube"
#     except Exception as e:
#         return f"Error playing YouTube: {str(e)}"

# # ==================== MUSIC FUNCTIONS ====================
# def PlayMusic(song_name=""):
#     """Play music on YouTube Music specifically"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return MobileOpenApp("youtube music")
    
#     try:
#         song_name = song_name.replace("on music", "").replace("music", "").replace("on youtube music", "").strip()
        
#         if not song_name or "random" in song_name.lower():
#             # Open YouTube Music with a popular Bollywood playlist
#             webopen("https://music.youtube.com/watch?v=4hzr6qLFTzI&list=RDAMVM4hzr6qLFTzI")
#             time.sleep(8)  # Wait for page to load
#             # Press space to play (single press only)
#             pyautogui.press('space')
#             return "Playing Bollywood music on YouTube Music"
#         else:
#             # Search for the specific song on YouTube Music
#             search_query = f"{song_name} site:music.youtube.com"
#             search(search_query)
#             time.sleep(5)
#             return f"Searching for {song_name} on YouTube Music"
            
#     except Exception as e:
#         return f"Error playing music: {str(e)}"

# def PlaySpotify(song_name=""):
#     """Spotify control"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return MobileOpenApp("spotify")
    
#     try:
#         song_name = song_name.replace("on spotify", "").replace("spotify", "").strip().lower()
        
#         if not song_name or "music" in song_name.lower():
#             webopen("https://open.spotify.com")
#             time.sleep(5)
#             pyautogui.press('space')
#             return "Playing music on Spotify"
#         else:
#             return PlayYoutube(song_name)
            
#     except Exception as e:
#         return f"Error controlling Spotify: {str(e)}"

# # ==================== BASIC FUNCTIONS ====================
# def GoogleSearch(Topic):
#     """Perform a Google search"""
#     search(Topic)
#     return f"Searched Google for: {Topic}"

# def YouTubeSearch(Topic):
#     """Search on YouTube"""
#     Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
#     webbrowser.open(Url4Search)
#     return f"Searched YouTube for: {Topic}"

# def Content(Topic):
#     """Generate and open content in Notepad"""
    
#     def OpenNotepad(File):
#         default_text_editor = "notepad.exe"
#         subprocess.Popen([default_text_editor, File])
        
#     def ContentWriterAI(prompt):
#         if not client:
#             return "Groq API not configured"
            
#         messages.append({"role": "user", "content": f"{prompt}."})
        
#         completion = client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=SystemChatBot + messages,
#             temperature=0.7,
#             max_tokens=2048,
#             top_p=1,
#             stream=True,
#             stop=None
#         )
        
#         Answer = ""
#         for chunk in completion:
#             if chunk.choices[0].delta.content:
#                 Answer += chunk.choices[0].delta.content
                
#         Answer = Answer.replace("</s>", "")
#         messages.append({"role": "assistant", "content": Answer})
#         return Answer
    
#     Topic = Topic.replace("Content ", "")
#     ContentByAI = ContentWriterAI(Topic)
    
#     os.makedirs("Data", exist_ok=True)
#     filename = f"Data/{Topic.lower().replace(' ', '')}.txt"
#     with open(filename, "w", encoding="utf-8") as file:
#         file.write(ContentByAI)
    
#     OpenNotepad(filename)
#     return f"Created content: {Topic}"

# # ==================== APP OPENING FUNCTION ====================
# def OpenApp(app_name, sess=requests.session()):
#     """Open application or website"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return MobileOpenApp(app_name)
        
#     app_name = app_name.lower().strip()
#     print(f"OPENING {app_name.upper()}")
    
#     if "youtube music" in app_name or "yt music" in app_name:
#         webopen("https://music.youtube.com")
#         print("Opening YouTube Music")
#         return "Opened YouTube Music"
    
#     try:
#         result = appopen(app_name, throw_error=True, match_closest=True)
#         if result:
#             return f"Opened {app_name}"
#     except Exception as e:
#         print(f"App not found locally: {e}")
    
#     website_map = {
#         "whatsapp": "https://web.whatsapp.com",
#         "instagram": "https://www.instagram.com",
#         "facebook": "https://www.facebook.com",
#         "telegram": "https://web.telegram.org",
#         "spotify": "https://open.spotify.com",
#         "netflix": "https://www.netflix.com",
#         "twitter": "https://twitter.com",
#         "linkedin": "https://www.linkedin.com",
#         "youtube": "https://www.youtube.com",
#         "gmail": "https://mail.google.com",
#         "chrome": "https://www.google.com",
#         "discord": "https://discord.com/app",
#         "youtube music": "https://music.youtube.com",
#         "yt music": "https://music.youtube.com"
#     }
    
#     if app_name in website_map:
#         webopen(website_map[app_name])
#         print(f"Opening {app_name.upper()} official website")
#         return f"Opened {app_name}"
    
#     return f"Could not open {app_name}"

# # ==================== CLOSE APP FUNCTION ====================
# def CloseApp(app_name):
#     """Close application safely"""
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return "Close app not supported on mobile"
    
#     protected_apps = ["python", "vscode", "pycharm", "cmd", "terminal", "assistant", "zyra", "main"]
    
#     if any(protected in app_name.lower() for protected in protected_apps):
#         return f"Cannot close {app_name} - protected application"
    
#     print(f"CLOSING {app_name.upper()}")
    
#     try:
#         if any(browser in app_name.lower() for browser in ["chrome", "youtube", "spotify", "web", "browser"]):
#             pyautogui.hotkey('ctrl', 'w')
#             time.sleep(1)
#             return f"Closed {app_name} tab"
#         else:
#             result = subprocess.run(['taskkill', '/f', '/im', f'{app_name}.exe'], 
#                                   capture_output=True, text=True, timeout=10)
#             if result.returncode == 0:
#                 return f"Closed {app_name}"
#             else:
#                 return f"Could not close {app_name}"
                
#     except Exception as e:
#         return f"Error closing {app_name}: {str(e)}"

# # ==================== FIXED SYSTEM CONTROL ====================
# def System(command):
#     """Fixed system control with proper mute handling"""
#     device_type = get_device_type()
#     if device_type == "mobile":
#         return "System commands not supported on mobile"
    
#     command = command.strip().lower()
    
#     # Handle media controls
#     if command in ["play", "pause", "next", "previous"]:
#         return MediaControl(command)
    
#     # Handle mute/unmute specifically
#     if command == "mute":
#         return set_volume(0)
#     elif command == "unmute":
#         return set_volume(50)  # Set to 50% when unmuting
    
#     # Handle volume commands with exact percentages
#     if any(word in command for word in ["volume", "vol"]):
#         numbers = [int(s) for s in command.split() if s.isdigit()]
        
#         if numbers:
#             level = min(max(numbers[0], 0), 100)
#             return set_volume(level)
#         elif "full" in command or "max" in command or "100" in command:
#             return set_volume(100)
#         elif "up" in command:
#             return "Use specific volume level like 'volume 50'"
#         elif "down" in command:
#             return "Use specific volume level like 'volume 30'"
    
#     # Other system commands
#     if command == "lock":
#         try:
#             subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
#             return "PC locked"
#         except Exception as e:
#             return f"Error locking PC: {e}"
            
#     elif command == "shutdown":
#         os.system("shutdown /s /t 10")
#         return "Shutting down computer in 10 seconds..."
            
#     elif command == "restart":
#         os.system("shutdown /r /t 1")
#         return "Restarting computer..."
    
#     return f"Unknown system command: {command}"

# # ==================== WHATSAPP FUNCTION ====================
# def SendMessage(contact, message_text=""):
#     """WhatsApp messaging"""
#     device_type = get_device_type()
#     if device_type == "mobile":
#         return MobileSendMessage(contact, message_text)
    
#     print(f"[MESSAGE] Sending to {contact}: {message_text}")
    
#     try:
#         phone_number = get_phone_number(contact)
#         if not phone_number:
#             phone_number = ''.join(filter(str.isdigit, contact))
        
#         if not phone_number:
#             webopen("https://web.whatsapp.com")
#             return f"Opened WhatsApp. Please search for '{contact}' and send: '{message_text}'"
        
#         phone_number = ''.join(filter(str.isdigit, phone_number))
#         if len(phone_number) == 10:
#             phone_number = '91' + phone_number
        
#         encoded_message = requests.utils.quote(message_text)
#         whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_message}"
        
#         webopen(whatsapp_url)
#         time.sleep(4)
#         pyautogui.press('enter')
#         time.sleep(2)
        
#         pyautogui.hotkey('ctrl', 'w')
        
#         return f"Message sent to {contact}"
        
#     except Exception as e:
#         return f"Error: {str(e)}. Please message manually."

# # ==================== CALLING FUNCTION ====================
# def CallContact(contact):
#     """Calling implementation"""
#     device_type = get_device_type()
#     if device_type == "mobile":
#         return MobileCall(contact)
    
#     print(f"[CALL] Calling: {contact}")
    
#     try:
#         phone_number = get_phone_number(contact)
#         if not phone_number:
#             phone_number = ''.join(filter(str.isdigit, contact))
        
#         if not phone_number:
#             return f"Could not find phone number for {contact}"
        
#         if len(phone_number) == 10:
#             phone_number = '91' + phone_number
        
#         webopen(f"tel:{phone_number}")
#         return f"Calling {contact} ({phone_number})"
        
#     except Exception as e:
#         return f"Error initiating call: {str(e)}"

# # ==================== COMMAND EXECUTION ====================
# async def ExecuteCommand(command):
#     """Execute a single command and return result"""
#     print(f"[AUTOMATION] Processing command: {command}")
    
#     if command in ["play", "pause", "next", "previous"]:
#         return MediaControl(command)
    
#     if command.startswith("open "):
#         app_name = command.removeprefix("open ").strip()
#         return OpenApp(app_name)
            
#     elif command.startswith("close "):
#         app_name = command.removeprefix("close ").strip()
#         return CloseApp(app_name)
        
#     elif command.startswith("play "):
#         song_name = command.removeprefix("play ").strip()
        
#         if "on spotify" in song_name.lower():
#             song_name = song_name.replace("on spotify", "").strip()
#             return PlaySpotify(song_name)
#         elif "on youtube music" in song_name.lower():
#             song_name = song_name.replace("on youtube music", "").strip()
#             return PlayMusic(song_name)
#         elif "on youtube" in song_name.lower():
#             song_name = song_name.replace("on youtube", "").strip()
#             return PlayYoutube(song_name)
#         elif "on music" in song_name.lower():
#             song_name = song_name.replace("on music", "").strip()
#             return PlayMusic(song_name)
#         elif "music" in song_name.lower() or not song_name:
#             return PlayMusic(song_name)
#         else:
#             return PlayYoutube(song_name)
        
#     elif command.startswith("content "):
#         return Content(command.removeprefix("content "))
        
#     elif command.startswith("google search "):
#         return GoogleSearch(command.removeprefix("google search "))
        
#     elif command.startswith("youtube search "):
#         return YouTubeSearch(command.removeprefix("youtube search "))
        
#     elif command.startswith("system "):
#         sys_command = command.removeprefix("system ")
#         sys_command = sys_command.replace("_", " ").strip()
#         return System(sys_command)
        
#     elif command.startswith("call "):
#         contact = command.removeprefix("call ")
#         return CallContact(contact)
        
#     elif command.startswith("message "):
#         parts = command.removeprefix("message ").split(" ", 1)
#         contact = parts[0]
#         message_text = parts[1] if len(parts) > 1 else ""
#         return SendMessage(contact, message_text)
        
#     elif command == "exit":
#         return "Exiting assistant"
        
#     else:
#         return f"No function found for: {command}"

# async def Automation(commands: list[str]):
#     """Main automation function - execute all commands and return results"""
#     results = []
    
#     for command in commands:
#         try:
#             result = await ExecuteCommand(command)
#             results.append(result)
#             print(f"[RESULT] {result}")
#         except Exception as e:
#             error_msg = f"Error executing '{command}': {str(e)}"
#             results.append(error_msg)
#             print(f"[ERROR] {error_msg}")
    
#     return results
        
# if __name__ == "__main__":
#     print("=== Automation.py Test Mode ===")
#     print("This file is meant to be imported, not run directly.")
#     print("To test, run your main application that calls the Automation() function.")