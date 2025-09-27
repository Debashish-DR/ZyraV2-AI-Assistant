from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import ExecuteCommand
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from Backend.ImageGeneration import GenerateImages
from dotenv import dotenv_values
import json
import os
import pymongo
import jwt
from datetime import datetime, timedelta
import time
import smtplib
from email.mime.text import MIMEText
import bcrypt
import random
import re

# ---------------------- ENV VARIABLES ---------------------- #
env_vars = dotenv_values(".env")
Functions = ["open", "close", "play", "google search", "youtube search", "system", "content", "call", "message", "reminder"]
JWT_SECRET = env_vars.get("JWT_SECRET", "fallback-secret-key-change-in-production")
SMTP_SERVER = env_vars.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(env_vars.get("SMTP_PORT", 587))
SMTP_USER = env_vars.get("SMTP_USER")
SMTP_PASS = env_vars.get("SMTP_PASS")
MONGODB_URI = env_vars.get("MONGODB_URI")

# Check if running on Render
IS_RENDER = os.environ.get('RENDER') is not None

# ---------------------- IMPROVED MONGODB SETUP ---------------------- #
try:
    # For Render.com MongoDB Atlas
    if IS_RENDER:
        # Use Render's environment variable
        MONGODB_URI = os.environ.get('MONGODB_URI')
        if not MONGODB_URI:
            print("❌ MONGODB_URI not found in environment variables")
            raise Exception("MongoDB URI not configured")
    else:
        # Local development
        MONGODB_URI = env_vars.get("MONGODB_URI")
    
    if not MONGODB_URI:
        raise Exception("MongoDB URI not configured")
    
    client = pymongo.MongoClient(MONGODB_URI, serverSelectionTimeoutMS=30000)
    
    # Test connection
    client.admin.command('ping')
    db = client['ai_assistant']
    users = db['users']
    
    # Create indexes
    users.create_index('email', unique=True)
    
    # Ensure chatlogs collection exists
    if 'chatlogs' not in db.list_collection_names():
        db.create_collection('chatlogs')
    
    print("✅ MongoDB connected successfully")
    print(f"✅ Database: {db.name}")
    
except Exception as e:
    print(f"❌ MongoDB connection error: {e}")
    print("🔄 Using fallback file-based storage")
    client = None
    db = None
    users = None

# ---------------------- CLOUD-COMPATIBLE CHAT LOG ---------------------- #
def sanitize_email(email):
    return re.sub(r'[^a-zA-Z0-9._-]', '_', email)

def get_user_chatlog_path(email):
    if not email:
        return "Data/ChatLog.json"
    
    sanitized_email = sanitize_email(email)
    return f"Data/ChatLog_{sanitized_email}.json"

def AppendToChatLog(role, content, email=None, message_id=None):
    if IS_RENDER and users is not None and email:
        # On Render, use MongoDB for chat logs
        try:
            chat_entry = {
                "email": email,
                "role": role,
                "content": content,
                "message_id": message_id or f"msg-{int(time.time()*1000)}-{random.randint(1000, 9999)}",
                "timestamp": datetime.utcnow()
            }
            db['chatlogs'].insert_one(chat_entry)
            return
        except Exception as e:
            print(f"Error saving to MongoDB: {e}")
    
    # Fallback to file system (for local development)
    chatlog_path = get_user_chatlog_path(email)
    try:
        os.makedirs("Data", exist_ok=True)
        if os.path.exists(chatlog_path):
            with open(chatlog_path, "r", encoding="utf-8") as file:
                chatlog_data = json.load(file)
        else:
            chatlog_data = []
    except (FileNotFoundError, json.JSONDecodeError):
        chatlog_data = []

    if not message_id:
        message_id = f"msg-{int(time.time()*1000)}-{random.randint(1000, 9999)}"

    chatlog_data.append({
        "role": role,
        "content": content,
        "id": message_id
    })

    with open(chatlog_path, "w", encoding="utf-8") as file:
        json.dump(chatlog_data, file, indent=4)

def ReadChatLogJson(email=None):
    if IS_RENDER and users is not None and email:
        try:
            chat_entries = db['chatlogs'].find({"email": email}).sort("timestamp", 1)
            return [{"role": entry["role"], "content": entry["content"], "id": entry["message_id"]} 
                   for entry in chat_entries]
        except Exception as e:
            print(f"Error reading from MongoDB: {e}")
    
    # Fallback to file system
    chatlog_path = get_user_chatlog_path(email)
    try:
        if os.path.exists(chatlog_path):
            with open(chatlog_path, "r", encoding="utf-8") as file:
                return json.load(file)
        else:
            return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def ShowDefaultChatIfNoChats(email=None):
    if IS_RENDER and users is not None and email:
        try:
            if db['chatlogs'].count_documents({"email": email}) == 0:
                AppendToChatLog("assistant", "Hello! I'm your virtual assistant. How can I help you today?", email)
        except:
            pass
    else:
        chatlog_path = get_user_chatlog_path(email)
        try:
            if not os.path.exists(chatlog_path) or os.path.getsize(chatlog_path) < 5:
                with open(chatlog_path, "w", encoding="utf-8") as file:
                    json.dump([], file, indent=4)
        except Exception:
            pass

def AnswerModifier(text):
    lines = text.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    return "\n".join(non_empty_lines)

def QueryModifier(query):
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

def ConvertModelDecisionToOldFormat(decision):
    old_format_commands = []
    
    for item in decision:
        if isinstance(item, dict):
            if item["name"] == "general_conversation":
                old_format_commands.append(f"general {item['parameters']['query']}")
            elif item["name"] == "realtime_information":
                old_format_commands.append(f"realtime {item['parameters']['query']}")
            elif item["name"] == "automation_task":
                action = item["parameters"]["action"]
                target = item["parameters"].get("target", "")
                if action in ["open", "close"]:
                    old_format_commands.append(f"{action} {target}")
                elif action in ["mute", "unmute", "volume_up", "volume_down", "lock", "shutdown", "close_all_tabs", "close_all_windows"]:
                    old_format_commands.append(f"system {action}")
            elif item["name"] == "web_search":
                engine = item["parameters"]["engine"]
                query = item["parameters"]["query"]
                old_format_commands.append(f"{engine} search {query}")
            elif item["name"] == "generate_image":
                old_format_commands.append(f"generate image {item['parameters']['prompt']}")
            elif item["name"] == "phone_control":
                action = item["parameters"]["action"]
                contact = item["parameters"]["contact"]
                if action == "call":
                    old_format_commands.append(f"call {contact}")
                elif action == "message":
                    message = item["parameters"].get("message", "")
                    old_format_commands.append(f"message {contact} {message}")
            elif item["name"] == "exit_assistant":
                old_format_commands.append("exit")
        elif isinstance(item, str):
            old_format_commands.append(item)
    
    return old_format_commands

def speak_automation_feedback(action_result, voice):
    if IS_RENDER:
        return  # Skip TTS on cloud for automation feedback
    
    feedback_phrases = {
        "open": "Opening {}",
        "close": "Closing {}",
        "play": "Playing {}",
        "system": "{}",
        "call": "Calling {}",
        "message": "Messaging {}"
    }
    
    for key, phrase in feedback_phrases.items():
        if action_result.lower().startswith(key):
            target = action_result.replace(key, "").strip()
            if target:
                feedback = phrase.format(target)
                TextToSpeech(feedback, voice)
                break

# ---------------------- FLASK SETUP ---------------------- #
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Cache for deduplication
response_cache = {}
last_tts_time = 0

# JWT verification middleware
def verify_token():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, jsonify({'error': 'Authorization header missing or invalid'}), 401
    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return decoded, None
    except jwt.ExpiredSignatureError:
        return None, jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return None, jsonify({'error': 'Invalid token'}), 401

@app.route('/')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Zyra AI Assistant',
        'environment': 'Render' if IS_RENDER else 'Local',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected' if users is not None else 'fallback_mode'
    })

# ---------------------- FIXED AUTHENTICATION ROUTES ---------------------- #
@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        username = data.get('username')
        
        print(f"🔧 Signup attempt: {email}, {username}")
        
        if not email or not password or not username:
            return jsonify({'error': 'Email, password, and username are required'}), 400
        
        # Check if MongoDB is connected
        if users is None:
            print("❌ MongoDB not connected")
            return jsonify({'error': 'Database connection failed. Please try again later.'}), 500
        
        # Check if user already exists
        existing_user = users.find_one({'email': email})
        if existing_user:
            print(f"❌ User already exists: {email}")
            return jsonify({'error': 'User already exists with this email'}), 400
        
        # Hash password properly
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user document
        user_data = {
            'email': email,
            'password': hashed_password,
            'username': username,
            'assistantname': 'Zyra',
            'assistantvoice': 'en-CA-ClaraNeural',
            'created_at': datetime.utcnow()
        }
        
        # Insert user
        result = users.insert_one(user_data)
        
        if result.inserted_id:
            print(f"✅ User created: {email} with ID: {result.inserted_id}")
            
            # Initialize user-specific chatlog
            ShowDefaultChatIfNoChats(email)
            
            # Generate JWT token
            token = jwt.encode({
                'email': email, 
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, JWT_SECRET, algorithm='HS256')
            
            return jsonify({
                'token': token, 
                'username': username, 
                'assistantname': 'Zyra', 
                'assistantvoice': 'en-CA-ClaraNeural',
                'message': 'Account created successfully'
            })
        else:
            print("❌ Failed to create user")
            return jsonify({'error': 'Failed to create account'}), 500
            
    except Exception as e:
        print(f"❌ Signup error: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        username = data.get('username')
        
        print(f"🔧 Login attempt: {email}")
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Check if MongoDB is connected
        if users is None:
            print("❌ MongoDB not connected - using fallback")
            return jsonify({'error': 'Service temporarily unavailable. Please try again.'}), 503
        
        # Find user
        user = users.find_one({'email': email})
        if not user:
            print(f"❌ User not found: {email}")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        print(f"✅ User found: {user['email']}")
        
        # Verify password
        try:
            password_valid = bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8'))
        except Exception as e:
            print(f"❌ Password check error: {e}")
            return jsonify({'error': 'Authentication error'}), 500
        
        if not password_valid:
            print("❌ Invalid password")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, JWT_SECRET, algorithm='HS256')
        
        print(f"✅ Login successful: {email}")
        
        return jsonify({
            'token': token,
            'username': user.get('username', 'User'),
            'assistantname': user.get('assistantname', 'Zyra'),
            'assistantvoice': user.get('assistantvoice', 'en-CA-ClaraNeural'),
            'message': 'Login successful'
        })
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({'error': 'Internal server error. Please try again.'}), 500

@app.route('/api/forgot', methods=['POST'])
def forgot_password():
    try:
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Check if MongoDB is connected
        if users is None:
            return jsonify({'error': 'Database connection failed. Please try again later.'}), 500
        
        user = users.find_one({'email': email})
        if not user:
            # Don't reveal whether email exists or not
            return jsonify({'message': 'If an account with that email exists, a reset link has been sent'})
        
        # Generate reset token
        reset_token = jwt.encode({
            'email': email,
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, JWT_SECRET, algorithm='HS256')
        
        # In a real application, you would send an email here
        # For now, we'll just return the token for testing
        if IS_RENDER:
            # On Render, we can't send emails easily, so return the token
            return jsonify({
                'message': 'Reset token generated (email simulation)',
                'reset_token': reset_token,  # Remove this in production
                'note': 'In production, this would be sent via email'
            })
        else:
            # Local development email sending
            frontend_url = "http://localhost:3000"
            reset_link = f"{frontend_url}/reset?token={reset_token}"
            
            msg = MIMEText(f"Click to reset your password: {reset_link}")
            msg['Subject'] = 'Zyra Password Reset'
            msg['From'] = SMTP_USER
            msg['To'] = email

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
            
            return jsonify({'message': 'Password reset link sent to your email'})
            
    except smtplib.SMTPAuthenticationError:
        return jsonify({'error': 'Email service configuration error'}), 500
    except Exception as e:
        print(f"Forgot password error: {e}")
        return jsonify({'error': 'Failed to process password reset request'}), 500

@app.route('/api/reset', methods=['POST'])
def reset_password():
    try:
        data = request.json
        token = data.get('token')
        new_password = data.get('new_password')
        
        if not token or not new_password:
            return jsonify({'error': 'Token and new password are required'}), 400
        
        try:
            # Verify token
            decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            email = decoded.get('email')
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Reset token has expired'}), 400
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid reset token'}), 400
        
        # Check if MongoDB is connected
        if users is None:
            return jsonify({'error': 'Database connection failed. Please try again later.'}), 500
        
        user = users.find_one({'email': email})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Hash new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update password
        users.update_one(
            {'email': email},
            {'$set': {'password': hashed_password}}
        )
        
        return jsonify({'message': 'Password reset successfully'})
        
    except Exception as e:
        print(f"Reset password error: {e}")
        return jsonify({'error': 'Failed to reset password'}), 500

@app.route('/api/settings', methods=['POST'])
def update_settings():
    try:
        decoded, error_response = verify_token()
        if error_response:
            return error_response
        data = request.json
        email = data.get('email')
        username = data.get('username')
        assistantname = data.get('assistantname')
        assistantvoice = data.get('assistantvoice')
        if not email or not username or not assistantname or not assistantvoice:
            return jsonify({'error': 'Email, username, assistantname, and assistantvoice required'}), 400
        if decoded['email'] != email:
            return jsonify({'error': 'Unauthorized email'}), 401
        if users is None:
            return jsonify({'error': 'Database connection failed'}), 500
            
        user = users.find_one({'email': email})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        users.update_one(
            {'email': email},
            {'$set': {
                'username': username,
                'assistantname': assistantname,
                'assistantvoice': assistantvoice
            }}
        )
        return jsonify({
            'message': 'Settings updated',
            'username': username,
            'assistantname': assistantname,
            'assistantvoice': assistantvoice
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-user-settings', methods=['POST'])
def get_user_settings():
    try:
        decoded, error_response = verify_token()
        if error_response:
            return error_response
        data = request.json
        email = data.get('email')
        if not email:
            return jsonify({'error': 'Email required'}), 400
        if decoded['email'] != email:
            return jsonify({'error': 'Unauthorized email'}), 401
        if users is None:
            return jsonify({'error': 'Database connection failed'}), 500
            
        user = users.find_one({'email': email})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'username': user.get('username', 'User'),
            'assistantname': user.get('assistantname', 'Zyra'),
            'assistantvoice': user.get('assistantvoice', 'en-CA-ClaraNeural'),
            'welcome_message': f"Hello, I'm {user.get('assistantname', 'Zyra')}, your virtual assistant. How can I help you today?"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/add-to-chatlog', methods=['POST'])
def add_to_chatlog():
    try:
        decoded, error_response = verify_token()
        if error_response:
            return error_response
        data = request.json
        role = data.get('role')
        content = data.get('content')
        email = data.get('email')
        message_id = data.get('id')
        
        if not role or not content or not email:
            return jsonify({'error': 'Role, content, and email required'}), 400
        
        if decoded['email'] != email:
            return jsonify({'error': 'Unauthorized email'}), 401
            
        AppendToChatLog(role, content, email, message_id)
        return jsonify({'message': 'Added to chatlog'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    global last_tts_time
    try:
        decoded, error_response = verify_token()
        if error_response:
            return error_response
        data = request.json
        message = data.get('message')
        email = data.get('email')
        if not message or not email:
            return jsonify({'error': 'Message and email required'}), 400
        if decoded['email'] != email:
            return jsonify({'error': 'Unauthorized email'}), 401
        
        # For cloud deployment, provide informative message about limitations
        if IS_RENDER:
            cloud_message = "🌐 **Cloud Assistant Mode**\n\n"
            cloud_message += "✅ *Working Features:* AI Chat, Web Search, Image Generation\n"
            cloud_message += "🔒 *Local-Only Features:* Voice Control, App Automation\n"
            cloud_message += "💡 *Tip:* Use text commands like 'search python' or 'generate image cat'\n\n"
            
            # Check if this is a system command that won't work on cloud
            system_commands = ['open ', 'close ', 'system ', 'call ', 'message ']
            if any(message.lower().startswith(cmd) for cmd in system_commands):
                return jsonify({
                    'reply': cloud_message + f"\n🔧 *Note:* '{message}' works on local Windows devices",
                    'status': 'Cloud Mode'
                })

        if users is not None:
            user = users.find_one({'email': email})
            if not user:
                return jsonify({'error': 'User not found'}), 404
            username = user.get('username', 'User')
            assistantname = user.get('assistantname', 'Zyra')
            assistantvoice = user.get('assistantvoice', 'en-CA-ClaraNeural')
        else:
            username = "User"
            assistantname = "Zyra"
            assistantvoice = "en-CA-ClaraNeural"

        cache_key = message.lower().strip()
        current_time = time.time()
        if cache_key in response_cache and current_time - response_cache[cache_key]['time'] < 5:
            return jsonify({'reply': response_cache[cache_key]['reply'], 'status': 'Answering ...'})

        AppendToChatLog("user", message, email)
        Decision = FirstLayerDMM(message)

        if Decision and isinstance(Decision[0], dict):
            Decision = ConvertModelDecisionToOldFormat(Decision)

        if not isinstance(Decision, list):
            Decision = [Decision] if Decision else ["general What?"]

        automation_results = []
        for query in Decision:
            if any(query.startswith(func) for func in Functions):
                result = ExecuteCommand(query)
                automation_results.append(result)
                if result and not result.startswith("Error") and not IS_RENDER:
                    speak_automation_feedback(result, assistantvoice)

        response = None
        if automation_results:
            response = " ".join(automation_results)
            if response and not response.startswith("Sorry") and not response.startswith("Error") and not response.startswith("Speech service"):
                AppendToChatLog("assistant", response, email)
        else:
            realtime_queries = [i for i in Decision if i.startswith("realtime")]
            general_queries = [i for i in Decision if i.startswith("general")]
            merged_query = " and ".join([" ".join(i.split()[1:]) for i in realtime_queries]) if realtime_queries else " ".join([" ".join(i.split()[1:]) for i in general_queries])

            if realtime_queries:
                response = RealtimeSearchEngine(QueryModifier(merged_query))
            elif general_queries:
                response = ChatBot(QueryModifier(merged_query), username, assistantname)
            else:
                for query in Decision:
                    if query.startswith("general"):
                        response = ChatBot(QueryModifier(query.replace("general", "", 1).strip(" .?!")), username, assistantname)
                        break
                    elif query.startswith("realtime"):
                        response = RealtimeSearchEngine(QueryModifier(query.replace("realtime", "", 1).strip(" .?!")))
                        break
                    elif "exit" in query:
                        response = "Okay, Bye!"
                    else:
                        response = "Sorry, I didn't understand that."
            
            if response and not response.startswith("Sorry") and not response.startswith("Error") and not response.startswith("Speech service"):
                AppendToChatLog("assistant", response, email)

        response_cache[cache_key] = {'reply': response, 'time': current_time}
        return jsonify({'reply': response, 'status': 'Answering ...'})
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/speech-to-text', methods=['POST'])
def speech_to_text():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        audio_path = 'Data/temp_audio.wav'
        os.makedirs("Data", exist_ok=True)
        audio_file.save(audio_path)
        
        # Check file size to avoid processing empty files
        if os.path.getsize(audio_path) < 1024:  # Less than 1KB
            os.remove(audio_path)
            return jsonify({'text': 'Sorry, I didn\'t catch that. Could you repeat?', 'status': 'Listening ...'})
        
        text = SpeechRecognition(audio_path)
        
        # Clean up
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
        return jsonify({'text': text, 'status': 'Listening ...'})
        
    except Exception as e:
        print(f"Speech-to-text error: {e}")
        # Clean up on error
        if os.path.exists(audio_path):
            os.remove(audio_path)
        return jsonify({'error': str(e), 'text': 'Sorry, I didn\'t catch that. Could you repeat?'}), 500

@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    global last_tts_time
    try:
        decoded, error_response = verify_token()
        if error_response:
            return error_response
        data = request.json
        text = data.get('text')
        email = data.get('email')
        if not text or not email:
            return jsonify({'error': 'Text and email required'}), 400
        if decoded['email'] != email:
            return jsonify({'error': 'Unauthorized email'}), 401
        if users is not None:
            user = users.find_one({'email': email})
            if not user:
                return jsonify({'error': 'User not found'}), 404
            assistantvoice = user.get('assistantvoice', 'en-CA-ClaraNeural')
        else:
            assistantvoice = 'en-CA-ClaraNeural'
        
        # FIXED: Check mute status from user settings
        is_muted = user.get('muted', False) if users is not None else False
        if is_muted:
            return jsonify({'error': 'Assistant is muted'}), 200
        
        current_time = time.time()
        cache_key = text.lower().strip()
        if cache_key in response_cache and current_time - response_cache[cache_key]['time'] < 5:
            if 'audio_path' in response_cache[cache_key]:
                return send_file(response_cache[cache_key]['audio_path'], mimetype='audio/mpeg')
        
        if current_time - last_tts_time > 2:
            audio_path = TextToSpeech(text, assistantvoice)
            if audio_path:
                response_cache[cache_key] = {'audio_path': audio_path, 'time': current_time}
                last_tts_time = current_time
                return send_file(audio_path, mimetype='audio/mpeg')
        return jsonify({'error': 'No audio generated'}), 500
    except Exception as e:
        print(f"TTS error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/image-generation', methods=['POST'])
def image_generation():
    try:
        prompt = request.json.get('prompt')
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        images = GenerateImages(prompt)
        if images:
            return jsonify({'images': images, 'status': 'Generated'})
        return jsonify({'error': 'No images generated'})
    except Exception as e:
        print(f"Image generation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-chatlog', methods=['POST'])
def get_chatlog():
    try:
        decoded, error_response = verify_token()
        if error_response:
            return error_response
        
        data = request.json
        email = data.get('email')
        if not email:
            return jsonify({'error': 'Email required'}), 400
            
        if decoded['email'] != email:
            return jsonify({'error': 'Unauthorized email'}), 401
            
        chatlog = ReadChatLogJson(email)
        print(f"DEBUG: Fetching chatlog for {email}, found {len(chatlog)} messages")
        return jsonify({'chatlog': chatlog})
    except Exception as e:
        print(f"Chatlog error: {e}")
        return jsonify({'chatlog': []})
@app.route('/')
def root():
    return jsonify({
        'status': 'healthy',
        'service': 'Zyra AI Assistant',
        'environment': 'Render' if IS_RENDER else 'Local',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected' if users is not None else 'fallback_mode',
        'endpoints': {
            'health': '/',
            'signup': '/api/signup',
            'login': '/api/login',
            'chat': '/api/chat',
            'settings': '/api/settings'
        }
    })

# Add this route to handle frontend deep links
@app.route('/<path:path>')
def catch_all(path):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/api/signup',
            '/api/login', 
            '/api/chat',
            '/api/settings',
            '/api/forgot',
            '/api/reset'
        ]
    }), 404

if __name__ == '__main__':
    # Create Data directory if it doesn't exist
    os.makedirs("Data", exist_ok=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=not IS_RENDER, host='0.0.0.0', port=port)




# from flask import Flask, request, jsonify, send_file
# from flask_cors import CORS
# from Backend.Model import FirstLayerDMM
# from Backend.RealtimeSearchEngine import RealtimeSearchEngine
# from Backend.Automation import ExecuteCommand
# from Backend.SpeechToText import SpeechRecognition
# from Backend.Chatbot import ChatBot
# from Backend.TextToSpeech import TextToSpeech
# from Backend.ImageGeneration import GenerateImages
# from dotenv import dotenv_values
# import json
# import os
# import pymongo
# import jwt
# from datetime import datetime, timedelta
# import time
# import smtplib
# from email.mime.text import MIMEText

# # ---------------------- ENV VARIABLES ---------------------- #
# env_vars = dotenv_values(".env")
# Functions = ["open", "close", "play", "google search", "youtube search", "system", "content", "call", "message", "reminder"]
# JWT_SECRET = env_vars.get("JWT_SECRET")
# SMTP_SERVER = env_vars.get("SMTP_SERVER", "smtp.gmail.com")
# SMTP_PORT = int(env_vars.get("SMTP_PORT", 587))
# SMTP_USER = env_vars.get("SMTP_USER")
# SMTP_PASS = env_vars.get("SMTP_PASS")
# MONGODB_URI = env_vars.get("MONGODB_URI")

# # MongoDB Setup
# client = pymongo.MongoClient(MONGODB_URI)
# db = client['ai_assistant']
# users = db['users']

# # ---------------------- CHAT LOG HELPERS (FIXED: NO DATE PROPERTY) ---------------------- #
# def TempDirectoryPath(filename):
#     return os.path.join("Data", filename)

# def AppendToChatLog(role, content):
#     try:
#         with open(r"Data\ChatLog.json", "r", encoding="utf-8") as file:
#             chatlog_data = json.load(file)
#     except (FileNotFoundError, json.JSONDecodeError):
#         chatlog_data = []

#     chatlog_data.append({"role": role, "content": content})  # REMOVED DATE PROPERTY

#     with open(r"Data\ChatLog.json", "w", encoding="utf-8") as file:
#         json.dump(chatlog_data, file, indent=4)

# def ShowDefaultChatIfNoChats():
#     try:
#         with open(r"Data\ChatLog.json", "r", encoding="utf-8") as file:
#             if len(file.read()) < 5:
#                 with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as f:
#                     f.write("")
#                 with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as f:
#                     f.write("")
#     except FileNotFoundError:
#         with open(r"Data\ChatLog.json", "w", encoding="utf-8") as file:
#             json.dump([], file)

# def ReadChatLogJson():
#     with open(r"Data\ChatLog.json", "r", encoding="utf-8") as file:
#         return json.load(file)

# def AnswerModifier(text):
#     lines = text.split("\n")
#     non_empty_lines = [line for line in lines if line.strip()]
#     return "\n".join(non_empty_lines)

# def QueryModifier(query):
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

# # Initialize chat log
# ShowDefaultChatIfNoChats()

# # ---------------------- CONVERT NEW FORMAT TO OLD FORMAT ---------------------- #
# def ConvertModelDecisionToOldFormat(decision):
#     old_format_commands = []
    
#     for item in decision:
#         if isinstance(item, dict):
#             if item["name"] == "general_conversation":
#                 old_format_commands.append(f"general {item['parameters']['query']}")
#             elif item["name"] == "realtime_information":
#                 old_format_commands.append(f"realtime {item['parameters']['query']}")
#             elif item["name"] == "automation_task":
#                 action = item["parameters"]["action"]
#                 target = item["parameters"].get("target", "")
#                 if action in ["open", "close"]:
#                     old_format_commands.append(f"{action} {target}")
#                 elif action in ["mute", "unmute", "volume_up", "volume_down", "lock", "shutdown", "close_all_tabs", "close_all_windows"]:
#                     old_format_commands.append(f"system {action}")
#             elif item["name"] == "web_search":
#                 engine = item["parameters"]["engine"]
#                 query = item["parameters"]["query"]
#                 old_format_commands.append(f"{engine} search {query}")
#             elif item["name"] == "generate_image":
#                 old_format_commands.append(f"generate image {item['parameters']['prompt']}")
#             elif item["name"] == "phone_control":
#                 action = item["parameters"]["action"]
#                 contact = item["parameters"]["contact"]
#                 if action == "call":
#                     old_format_commands.append(f"call {contact}")
#                 elif action == "message":
#                     message = item["parameters"].get("message", "")
#                     old_format_commands.append(f"message {contact} {message}")
#             elif item["name"] == "exit_assistant":
#                 old_format_commands.append("exit")
#         elif isinstance(item, str):
#             old_format_commands.append(item)
    
#     return old_format_commands

# # ---------------------- FLASK SETUP ---------------------- #
# app = Flask(__name__)
# CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# # Cache for deduplication
# response_cache = {}
# last_tts_time = 0  # Global TTS debounce

# # JWT verification middleware
# def verify_token():
#     auth_header = request.headers.get('Authorization')
#     if not auth_header or not auth_header.startswith('Bearer '):
#         return None, jsonify({'error': 'Authorization header missing or invalid'}), 401
#     token = auth_header.split(' ')[1]
#     try:
#         decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
#         return decoded, None
#     except jwt.ExpiredSignatureError:
#         return None, jsonify({'error': 'Token has expired'}), 401
#     except jwt.InvalidTokenError:
#         return None, jsonify({'error': 'Invalid token'}), 401

# @app.route('/api/signup', methods=['POST'])
# def signup():
#     try:
#         data = request.json
#         email = data.get('email')
#         password = data.get('password')
#         username = data.get('username')
#         if not email or not password or not username:
#             return jsonify({'error': 'Email, password, and username required'}), 400
#         if users.find_one({'email': email}):
#             return jsonify({'error': 'User already exists'}), 400
#         users.insert_one({
#             'email': email,
#             'password': password,  # Hash in prod
#             'username': username,
#             'assistantname': 'Zyra',  # Default
#             'assistantvoice': 'en-CA-ClaraNeural'  # Default
#         })
#         token = jwt.encode({'email': email, 'exp': datetime.utcnow() + timedelta(hours=24)}, JWT_SECRET)
#         return jsonify({'token': token, 'username': username, 'assistantname': 'Zyra', 'assistantvoice': 'en-CA-ClaraNeural'})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/login', methods=['POST'])
# def login():
#     try:
#         data = request.json
#         email = data.get('email')
#         password = data.get('password')
#         username = data.get('username')
#         if not email or not password or not username:
#             return jsonify({'error': 'Email, password, and username required'}), 400
#         user = users.find_one({'email': email, 'password': password})  # Hash in prod
#         if user:
#             users.update_one({'email': email}, {'$set': {'username': username}})
#             token = jwt.encode({'email': email, 'exp': datetime.utcnow() + timedelta(hours=24)}, JWT_SECRET)
#             return jsonify({
#                 'token': token,
#                 'username': username,
#                 'assistantname': user.get('assistantname', 'Zyra'),
#                 'assistantvoice': user.get('assistantvoice', 'en-CA-ClaraNeural')
#             })
#         return jsonify({'error': 'Invalid credentials'}), 401
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/settings', methods=['POST'])
# def update_settings():
#     try:
#         decoded, error_response = verify_token()
#         if error_response:
#             return error_response
#         data = request.json
#         email = data.get('email')
#         username = data.get('username')
#         assistantname = data.get('assistantname')
#         assistantvoice = data.get('assistantvoice')
#         if not email or not username or not assistantname or not assistantvoice:
#             return jsonify({'error': 'Email, username, assistantname, and assistantvoice required'}), 400
#         if decoded['email'] != email:
#             return jsonify({'error': 'Unauthorized email'}), 401
#         user = users.find_one({'email': email})
#         if not user:
#             return jsonify({'error': 'User not found'}), 404
#         users.update_one(
#             {'email': email},
#             {'$set': {
#                 'username': username,
#                 'assistantname': assistantname,
#                 'assistantvoice': assistantvoice
#             }}
#         )
#         return jsonify({
#             'message': 'Settings updated',
#             'username': username,
#             'assistantname': assistantname,
#             'assistantvoice': assistantvoice
#         })
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/get-user-settings', methods=['POST'])
# def get_user_settings():
#     try:
#         decoded, error_response = verify_token()
#         if error_response:
#             return error_response
#         data = request.json
#         email = data.get('email')
#         if not email:
#             return jsonify({'error': 'Email required'}), 400
#         if decoded['email'] != email:
#             return jsonify({'error': 'Unauthorized email'}), 401
#         user = users.find_one({'email': email})
#         if not user:
#             return jsonify({'error': 'User not found'}), 404
#         return jsonify({
#             'username': user.get('username', 'User'),
#             'assistantname': user.get('assistantname', 'Zyra'),
#             'assistantvoice': user.get('assistantvoice', 'en-CA-ClaraNeural')
#         })
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/add-to-chatlog', methods=['POST'])
# def add_to_chatlog():
#     try:
#         data = request.json
#         role = data.get('role')
#         content = data.get('content')
#         if not role or not content:
#             return jsonify({'error': 'Role and content required'}), 400
#         AppendToChatLog(role, content)
#         return jsonify({'message': 'Added to chatlog'})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/forgot', methods=['POST'])
# def forgot_password():
#     try:
#         data = request.json
#         email = data.get('email')
#         if not email:
#             return jsonify({'error': 'Email required'}), 400
#         user = users.find_one({'email': email})
#         if not user:
#             return jsonify({'error': 'User not found'}), 404
        
#         reset_token = jwt.encode(
#             {'email': email, 'exp': datetime.utcnow() + timedelta(minutes=30)},
#             JWT_SECRET
#         )
        
#         msg = MIMEText(f"Click to reset your password: http://localhost:3000/reset?token={reset_token}")
#         msg['Subject'] = 'Zyra Password Reset'
#         msg['From'] = SMTP_USER
#         msg['To'] = email

#         with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#             server.starttls()
#             server.login(SMTP_USER, SMTP_PASS)
#             server.send_message(msg)
        
#         return jsonify({'message': 'Reset link sent to your email'})
#     except smtplib.SMTPAuthenticationError:
#         return jsonify({'error': 'Invalid SMTP credentials'}), 500
#     except Exception as e:
#         return jsonify({'error': f'Failed to send email: {str(e)}'}), 500

# @app.route('/api/reset', methods=['POST'])
# def reset_password():
#     try:
#         data = request.json
#         token = data.get('token')
#         new_password = data.get('new_password')
#         if not token or not new_password:
#             return jsonify({'error': 'Token and new password required'}), 400
#         try:
#             decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
#             email = decoded.get('email')
#         except jwt.ExpiredSignatureError:
#             return jsonify({'error': 'Token has expired'}), 400
#         except jwt.InvalidTokenError:
#             return jsonify({'error': 'Invalid token'}), 400
#         user = users.find_one({'email': email})
#         if not user:
#             return jsonify({'error': 'User not found'}), 404
#         users.update_one(
#             {'email': email},
#             {'$set': {'password': new_password}}  # Hash in prod
#         )
#         return jsonify({'message': 'Password reset successfully'})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/chat', methods=['POST'])
# def chat():
#     global last_tts_time  # FIXED: Global TTS debounce
#     try:
#         decoded, error_response = verify_token()
#         if error_response:
#             return error_response
#         data = request.json
#         message = data.get('message')
#         email = data.get('email')
#         if not message or not email:
#             return jsonify({'error': 'Message and email required'}), 400
#         if decoded['email'] != email:
#             return jsonify({'error': 'Unauthorized email'}), 401
#         user = users.find_one({'email': email})
#         if not user:
#             return jsonify({'error': 'User not found'}), 404
#         username = user.get('username', 'User')
#         assistantname = user.get('assistantname', 'Zyra')

#         cache_key = message.lower().strip()
#         current_time = time.time()
#         if cache_key in response_cache and current_time - response_cache[cache_key]['time'] < 5:
#             return jsonify({'reply': response_cache[cache_key]['reply'], 'status': 'Answering ...'})

#         # FIXED: Only call TTS once
#         AppendToChatLog("user", message)
#         Decision = FirstLayerDMM(message)

#         if Decision and isinstance(Decision[0], dict):
#             Decision = ConvertModelDecisionToOldFormat(Decision)

#         if not isinstance(Decision, list):
#             Decision = [Decision] if Decision else ["general What?"]

#         automation_results = []
#         for query in Decision:
#             if any(query.startswith(func) for func in Functions):
#                 result = ExecuteCommand(query)
#                 automation_results.append(result)

#         if automation_results:
#             response = " ".join(automation_results)
#             AppendToChatLog("assistant", response)
#             # FIXED: Single TTS call with debounce
#             if current_time - last_tts_time > 2:  # 2 second debounce
#                 TextToSpeech(response, user.get('assistantvoice', 'en-CA-ClaraNeural'))
#                 last_tts_time = current_time
#             response_cache[cache_key] = {'reply': response, 'time': current_time}
#             return jsonify({'reply': response, 'status': 'Answering ...'})

#         realtime_queries = [i for i in Decision if i.startswith("realtime")]
#         general_queries = [i for i in Decision if i.startswith("general")]
#         merged_query = " and ".join([" ".join(i.split()[1:]) for i in realtime_queries]) if realtime_queries else " ".join([" ".join(i.split()[1:]) for i in general_queries])

#         if realtime_queries:
#             response = RealtimeSearchEngine(QueryModifier(merged_query))
#         elif general_queries:
#             response = ChatBot(QueryModifier(merged_query), username, assistantname)
#         else:
#             for query in Decision:
#                 if query.startswith("general"):
#                     response = ChatBot(QueryModifier(query.replace("general", "", 1).strip(" .?!")), username, assistantname)
#                     break
#                 elif query.startswith("realtime"):
#                     response = RealtimeSearchEngine(QueryModifier(query.replace("realtime", "", 1).strip(" .?!")))
#                     break
#                 elif "exit" in query:
#                     response = "Okay, Bye!"
#                     AppendToChatLog("assistant", response)
#                     if current_time - last_tts_time > 2:
#                         TextToSpeech(response, user.get('assistantvoice', 'en-CA-ClaraNeural'))
#                         last_tts_time = current_time
#                     response_cache[cache_key] = {'reply': response, 'time': current_time}
#                     return jsonify({'reply': response, 'status': 'Answering ...'})
#                 else:
#                     response = "Sorry, I didn't understand that."
        
#         AppendToChatLog("assistant", response)
#         # FIXED: Single TTS call with debounce
#         if current_time - last_tts_time > 2:  # 2 second debounce
#             TextToSpeech(response, user.get('assistantvoice', 'en-CA-ClaraNeural'))
#             last_tts_time = current_time
#         response_cache[cache_key] = {'reply': response, 'time': current_time}
#         return jsonify({'reply': response, 'status': 'Answering ...'})
#     except Exception as e:
#         print(f"Chat error: {e}")  # FIXED: Better error logging
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/speech-to-text', methods=['POST'])
# def speech_to_text():
#     try:
#         if 'audio' not in request.files:
#             return jsonify({'error': 'No audio file provided'}), 400
#         audio_file = request.files['audio']
#         audio_path = 'Data/temp_audio.wav'
#         os.makedirs("Data", exist_ok=True)
#         audio_file.save(audio_path)
#         text = SpeechRecognition(audio_path)
#         os.remove(audio_path)
#         AppendToChatLog("user", text)
#         return jsonify({'text': text, 'status': 'Listening ...'})
#     except Exception as e:
#         print(f"Speech-to-text error: {e}")
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/text-to-speech', methods=['POST'])
# def text_to_speech():
#     global last_tts_time  # FIXED: Global debounce
#     try:
#         decoded, error_response = verify_token()
#         if error_response:
#             return error_response
#         data = request.json
#         text = data.get('text')
#         email = data.get('email')
#         if not text or not email:
#             return jsonify({'error': 'Text and email required'}), 400
#         if decoded['email'] != email:
#             return jsonify({'error': 'Unauthorized email'}), 401
#         user = users.find_one({'email': email})
#         if not user:
#             return jsonify({'error': 'User not found'}), 404
        
#         current_time = time.time()
#         cache_key = text.lower().strip()
#         if cache_key in response_cache and current_time - response_cache[cache_key]['time'] < 5:
#             if 'audio_path' in response_cache[cache_key]:
#                 return send_file(response_cache[cache_key]['audio_path'], mimetype='audio/mpeg')
        
#         # FIXED: Use global debounce
#         if current_time - last_tts_time > 2:
#             audio_path = TextToSpeech(text, user.get('assistantvoice', 'en-CA-ClaraNeural'))
#             if audio_path:
#                 response_cache[cache_key] = {'audio_path': audio_path, 'time': current_time}
#                 last_tts_time = current_time
#                 return send_file(audio_path, mimetype='audio/mpeg')
#         return jsonify({'error': 'No audio generated'}), 500
#     except Exception as e:
#         print(f"TTS error: {e}")
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/image-generation', methods=['POST'])
# def image_generation():
#     try:
#         prompt = request.json.get('prompt')
#         if not prompt:
#             return jsonify({'error': 'No prompt provided'}), 400
#         images = GenerateImages(prompt)
#         if images:
#             return jsonify({'images': images, 'status': 'Generated'})
#         return jsonify({'error': 'No images generated'})
#     except Exception as e:
#         print(f"Image generation error: {e}")
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/get-chatlog', methods=['GET'])
# def get_chatlog():
#     try:
#         chatlog = ReadChatLogJson()
#         return jsonify({'chatlog': chatlog})
#     except Exception as e:
#         print(f"Chatlog error: {e}")
#         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)




#=======================================main code==========================================#
# from Frontend.GUI import (
#     GraphicalUserInterface,
#     SetAssistantStatus,
#     ShowTextToScreen,
#     TempDirectoryPath,
#     SetMicrophoneStatus,
#     AnswerModifier,
#     QueryModifier,
#     GetMicrophoneStatus,
#     GetAssistantStatus
# )

# from Backend.Model import FirstLayerDMM
# from Backend.RealtimeSearchEngine import RealtimeSearchEngine
# from Backend.Automation import Automation, ExecuteCommand
# from Backend.SpeechToText import SpeechRecognition
# from Backend.Chatbot import ChatBot
# from Backend.TextToSpeech import TextToSpeech
# from dotenv import dotenv_values
# from asyncio import run
# from time import sleep
# import subprocess
# import threading
# import json
# import os

# # ---------------------- ENV VARIABLES ---------------------- #
# env_vars = dotenv_values(".env")
# Username = env_vars.get("Username")
# Assistantname = env_vars.get("Assistantname")
# DefaultMessage = f'''{Username} : Hello {Assistantname} How are you?
# {Assistantname} : Welcome {Username}. I am doing well. How can I help you?'''
# subprocesses = []
# Functions = ["open", "close", "play", "google search", "youtube search", "system", "content", "call", "message", "reminder"]

# # ---------------------- CHAT LOG HELPERS ---------------------- #
# def AppendToChatLog(role, content):
#     """Append a user/assistant message into ChatLog.json"""
#     try:
#         with open(r"Data\\ChatLog.json", "r", encoding="utf-8") as file:
#             chatlog_data = json.load(file)
#     except (FileNotFoundError, json.JSONDecodeError):
#         chatlog_data = []

#     chatlog_data.append({"role": role, "content": content})

#     with open(r"Data\\ChatLog.json", "w", encoding="utf-8") as file:
#         json.dump(chatlog_data, file, indent=4)

#     # update UI file immediately after append
#     ChatLogIntegration()


# def ShowDefaultChatIfNoChats():
#     try:
#         with open(r"Data\\ChatLog.json", "r", encoding="utf-8") as file:
#             if len(file.read()) < 5:
#                 with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as f:
#                     f.write("")
#                 with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as f:
#                     f.write(DefaultMessage)
#     except FileNotFoundError:
#         with open(r"Data\\ChatLog.json", "w", encoding="utf-8") as file:
#             json.dump([], file)


# def ReadChatLogJson():
#     with open(r"Data\\ChatLog.json", "r", encoding="utf-8") as file:
#         return json.load(file)


# def ChatLogIntegration():
#     """Convert JSON chat into displayable text for GUI"""
#     json_data = ReadChatLogJson()
#     formatted_chatlog = ""

#     for entry in json_data:
#         if entry["role"] == "user":
#             formatted_chatlog += f"{Username}: {entry['content']}\n"
#         elif entry["role"] == "assistant":
#             formatted_chatlog += f"{Assistantname}: {entry['content']}\n"

#     with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
#         file.write(AnswerModifier(formatted_chatlog))

#     with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
#         file.write(AnswerModifier(formatted_chatlog))


# def InitialExecution():
#     SetMicrophoneStatus("False")
#     ShowTextToScreen("")
#     ShowDefaultChatIfNoChats()
#     ChatLogIntegration()


# InitialExecution()

# # ---------------------- NEW: CONVERT NEW FORMAT TO OLD FORMAT ---------------------- #
# def ConvertModelDecisionToOldFormat(decision):
#     """
#     Convert new model format [{"name": "open_app", "parameters": {...}}] 
#     to old format ["open chrome", "general hello"] for backward compatibility
#     """
#     old_format_commands = []
    
#     for item in decision:
#         if isinstance(item, dict):  # New format
#             if item["name"] == "general_conversation":
#                 old_format_commands.append(f"general {item['parameters']['query']}")
#             elif item["name"] == "realtime_information":
#                 old_format_commands.append(f"realtime {item['parameters']['query']}")
#             elif item["name"] == "automation_task":
#                 action = item["parameters"]["action"]
#                 target = item["parameters"].get("target", "")
#                 if action in ["open", "close"]:
#                     old_format_commands.append(f"{action} {target}")
#                 elif action in ["mute", "unmute", "volume_up", "volume_down", "lock", "shutdown", "close_all_tabs", "close_all_windows"]:
#                     old_format_commands.append(f"system {action}")
#             elif item["name"] == "web_search":
#                 engine = item["parameters"]["engine"]
#                 query = item["parameters"]["query"]
#                 old_format_commands.append(f"{engine} search {query}")
#             elif item["name"] == "generate_image":
#                 old_format_commands.append(f"generate image {item['parameters']['prompt']}")
#             elif item["name"] == "phone_control":
#                 action = item["parameters"]["action"]
#                 contact = item["parameters"]["contact"]
#                 if action == "call":
#                     old_format_commands.append(f"call {contact}")
#                 elif action == "message":
#                     message = item["parameters"].get("message", "")
#                     old_format_commands.append(f"message {contact} {message}")
#             elif item["name"] == "exit_assistant":
#                 old_format_commands.append("exit")
                
#         elif isinstance(item, str):  # Old format (fallback)
#             old_format_commands.append(item)
    
#     return old_format_commands

# # ---------------------- MAIN EXECUTION ---------------------- #
# async def MainExecution():
#     TaskExecution = False
#     ImageExecution = False
#     ImageGenerationQuery = ""

#     SetAssistantStatus("Listening ...")
#     Query = SpeechRecognition()

#     # USER MESSAGE → show + log once
#     AppendToChatLog("user", Query)
#     ShowTextToScreen(f"{Username}: {Query}")

#     SetAssistantStatus("Processing ...")
#     Decision = FirstLayerDMM(Query)

#     print("\nRaw Decision :", Decision, "\n")
    
#     # NEW: Convert new format to old format for backward compatibility
#     if Decision and isinstance(Decision[0], dict):
#         Decision = ConvertModelDecisionToOldFormat(Decision)
#         print("Converted Decision :", Decision, "\n")

#     # Decision safeguard
#     if not isinstance(Decision, list):
#         Decision = [Decision] if Decision else ["general What?"]

#     # First, handle automation tasks (but don't break flow for answers)
#     automation_results = []
#     for queries in Decision:
#         if any(queries.startswith(func) for func in Functions):
#             single_result = await ExecuteCommand(queries)
#             automation_results.append(single_result)
#             TaskExecution = True

#     if automation_results:
#         for result in automation_results:
#             AppendToChatLog("assistant", result)
#             ShowTextToScreen(f"{Assistantname}: {result}")
#             TextToSpeech(result)

#     # Then, handle realtime/general (as before, but use only realtime parts for search)
#     realtime_queries = [i for i in Decision if i.startswith("realtime")]
#     general_queries = [i for i in Decision if i.startswith("general")]
#     Merged_query = " and ".join([" ".join(i.split()[1:]) for i in realtime_queries]) if realtime_queries else " ".join([" ".join(i.split()[1:]) for i in general_queries])

#     # ---------------------- Image Generation ---------------------- #
#     for queries in Decision:
#         if "generate image" in queries:
#             ImageGenerationQuery = queries
#             ImageExecution = True

#     if ImageExecution:
#         prompt_clean = ImageGenerationQuery.replace("generate image", "").strip().replace(" ", "_")
#         data_file = r"Frontend\Files\ImageGeneration.data"
#         try:
#             with open(data_file, "r") as f:
#                 file_content = f.read().strip()
#             print(f"[DEBUG] ImageGeneration.data content: {file_content}")
#         except Exception as e:
#             print(f"[DEBUG] Error reading ImageGeneration.data: {str(e)}")
#         with open(data_file, "w") as f:
#             f.write(f"{ImageGenerationQuery},True")
#             f.flush()  # Ensure write is committed
#         sleep(0.1)  # Brief delay to ensure file is written
#         try:
#             print("[DEBUG] Starting ImageGeneration.py subprocess...")
#             p1 = subprocess.Popen(['python', r'Backend\ImageGeneration.py'],
#                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
#                                   stdin=subprocess.PIPE, shell=False)
#             subprocesses.append(p1)
#             try:
#                 stdout, stderr = p1.communicate(timeout=90)
#                 stdout = stdout.decode('utf-8') if stdout else ""
#                 stderr = stderr.decode('utf-8') if stderr else ""
#                 return_code = p1.returncode
#                 print(f"[DEBUG] Subprocess return code: {return_code}")
#                 if stderr:
#                     error_msg = f"Image generation error: {stderr[:100]}"
#                     AppendToChatLog("assistant", error_msg)
#                     ShowTextToScreen(f"{Assistantname}: {error_msg}")
#                     TextToSpeech(error_msg)
#                 elif "Generated" in stdout:
#                     image_dir = r"Data"
#                     image_files = [f for f in os.listdir(image_dir) if f.startswith(prompt_clean) and f.endswith(".jpg")] if os.path.exists(image_dir) else []
#                     if image_files:
#                         latest_image = max([os.path.join(image_dir, f) for f in image_files], key=os.path.getctime, default="")
#                         success_msg = f"Images generated and saved: {latest_image}"
#                         AppendToChatLog("assistant", success_msg)
#                         ShowTextToScreen(f"{Assistantname}: {success_msg}")
#                         TextToSpeech(success_msg)
#                     else:
#                         error_msg = "Image generation completed but no images found in Data folder."
#                         AppendToChatLog("assistant", error_msg)
#                         ShowTextToScreen(f"{Assistantname}: {error_msg}")
#                         TextToSpeech(error_msg)
#                 else:
#                     error_msg = f"Image generation failed: No output from subprocess (return code: {return_code}). Check ImageGeneration.data or API key."
#                     AppendToChatLog("assistant", error_msg)
#                     ShowTextToScreen(f"{Assistantname}: {error_msg}")
#                     TextToSpeech(error_msg)
#             except subprocess.TimeoutExpired:
#                 p1.terminate()
#                 error_msg = "Image generation timed out after 90 seconds."
#                 AppendToChatLog("assistant", error_msg)
#                 ShowTextToScreen(f"{Assistantname}: {error_msg}")
#                 TextToSpeech(error_msg)
#         except Exception as e:
#             error_msg = f"Image generation unavailable: {str(e)}"
#             AppendToChatLog("assistant", error_msg)
#             ShowTextToScreen(f"{Assistantname}: {error_msg}")
#             TextToSpeech(error_msg)

#     # ---------------------- AI RESPONSE ---------------------- #
#     Answer = None

#     if realtime_queries:
#         SetAssistantStatus("Searching ...")
#         Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
#     elif general_queries:
#         SetAssistantStatus("Processing ...")
#         Answer = ChatBot(QueryModifier(Merged_query))

#     else:
#         for Queries in Decision:
#             Qraw = str(Queries).strip().lower()

#             if Qraw.startswith("general"):
#                 SetAssistantStatus("Processing ...")
#                 QueryFinal = Qraw.replace("general", "", 1).strip(" .?!")
#                 Answer = ChatBot(QueryModifier(QueryFinal))
#                 break

#             elif Qraw.startswith("realtime"):
#                 SetAssistantStatus("Searching ...")
#                 QueryFinal = Qraw.replace("realtime", "", 1).strip(" .?!")
#                 Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
#                 break

#             elif "exit" in Qraw:
#                 Answer = "Okay, Bye!"
#                 AppendToChatLog("assistant", Answer)
#                 ShowTextToScreen(f"{Assistantname}: {Answer}")
#                 SetAssistantStatus("Answering ...")
#                 TextToSpeech(Answer)
#                 os._exit(1)

#     # ---------------------- Final assistant response ---------------------- #
#     if Answer:
#         AppendToChatLog("assistant", Answer)
#         ShowTextToScreen(f"{Assistantname}: {Answer}")
#         SetAssistantStatus("Answering ...")
#         TextToSpeech(Answer)

#     return True

# # ---------------------- THREADS ---------------------- #
# def FirstThread():
#     while True:
#         if GetMicrophoneStatus() == "True":
#             run(MainExecution())
#         else:
#             if "Available ..." not in GetAssistantStatus():
#                 SetAssistantStatus("Available ...")
#             sleep(0.1)


# def SecondThread():
#     GraphicalUserInterface()


# if __name__ == "__main__":
#     thread2 = threading.Thread(target=FirstThread, daemon=True)
#     thread2.start()
#     SecondThread()



#=======================================main code==========================================#
