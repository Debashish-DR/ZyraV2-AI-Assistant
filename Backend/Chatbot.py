
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import time
import pymongo
import os

# Cloud-friendly environment variable loading
def load_env_vars():
    # Priority 1: Render environment variables (for cloud)
    groq_key = os.environ.get('GroqAPIKey') or os.environ.get('GROQ_API_KEY')
    mongodb_uri = os.environ.get('MONGODB_URI')
    
    # Priority 2: .env file (for local development)
    if not groq_key or not mongodb_uri:
        try:
            env_vars = dotenv_values(".env")
            groq_key = groq_key or env_vars.get("GroqAPIKey")
            mongodb_uri = mongodb_uri or env_vars.get("MONGODB_URI")
        except:
            pass
    
    return groq_key, mongodb_uri

GroqAPIKey, MONGODB_URI = load_env_vars()

# FIXED: Safer Groq client initialization
def get_groq_client():
    """Safely initialize Groq client with error handling"""
    if not GroqAPIKey:
        print("⚠️ GroqAPIKey not set - AI features disabled")
        return None
    
    try:
        # Use a simpler initialization approach
        client = Groq(api_key=GroqAPIKey)
        print("✅ Groq client initialized successfully")
        return client
    except Exception as e:
        print(f"❌ Groq client initialization failed: {e}")
        return None

# Initialize clients safely
client = get_groq_client()

# Rest of your existing Chatbot.py code remains the same...
if MONGODB_URI:
    try:
        mongo_client = pymongo.MongoClient(MONGODB_URI)
        db = mongo_client['ai_assistant']
        users = db['users']
        print("✅ MongoDB connected successfully")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        mongo_client = None
        db = None
        users = None
else:
    mongo_client = None
    db = None
    users = None
    print("⚠️ MONGODB_URI not set - Database features disabled")

# FIXED: Safe file loading function
def load_chatlog():
    """Safely load chatlog with proper error handling"""
    try:
        # Create Data directory if it doesn't exist
        os.makedirs("Data", exist_ok=True)
        
        chatlog_path = "Data/ChatLog.json"
        
        if os.path.exists(chatlog_path):
            with open(chatlog_path, "r", encoding="utf-8") as f:
                return load(f)
        else:
            # Create empty chatlog file
            with open(chatlog_path, "w", encoding="utf-8") as f:
                dump([], f, indent=4)
            print("📁 Created new ChatLog.json file")
            return []
    except Exception as e:
        print(f"❌ Error reading ChatLog.json: {e}")
        return []

def save_chatlog(messages):
    """Safely save chatlog with proper error handling"""
    try:
        os.makedirs("Data", exist_ok=True)
        chatlog_path = "Data/ChatLog.json"
        
        with open(chatlog_path, "w", encoding="utf-8") as f:
            dump(messages, f, indent=4)
    except Exception as e:
        print(f"❌ Error saving ChatLog.json: {e}")

response_cache = {}  # Cache for deduplication

def RealtimeInformation():
    """Get current date and time information"""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    
    data = f"Please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Hour: {hour}\nMinute: {minute}\nSecond: {second}\n"
    return data

def AnswerModifier(Answer):
    """Clean up the answer by removing empty lines"""
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer

def ChatBot(Query, username, assistantname):
    """Main chatbot function with Groq integration"""
    
    # Check if Groq client is available
    if not client:
        return "🤖 **AI Assistant Notice**\n\n" + \
               "🔸 *AI chat features require Groq API key setup* \n" + \
               "🔸 *All other commands work: 'open youtube', 'play music', etc.* \n\n" + \
               "🚀 **To enable AI features:**\n" + \
               "1. Add 'GroqAPIKey' to Render environment variables\n" + \
               "2. Your app will automatically enable AI mode!\n\n" + \
               "💬 *Try these commands now: 'open youtube', 'play music', 'google search python'*"
    
    try:
        # Check cache for duplicate queries
        cache_key = Query.lower().strip()
        current_time = time.time()
        if cache_key in response_cache and current_time - response_cache[cache_key]['time'] < 5:
            print(f"✅ Returning cached response for query: {Query}")
            return response_cache[cache_key]['answer']

        # System prompt
        System = f"""Hello, I am {username}, You are a very accurate and advanced AI chatbot named {assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""
        SystemChatBot = [{"role": "system", "content": System}]

        # FIXED: Load messages safely
        messages = load_chatlog()
        print(f"📖 Loaded {len(messages)} messages from chatlog")

        # Prepare messages for Groq API (only role and content)
        groq_messages = []
        for msg in messages:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                groq_messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current query
        groq_messages.append({"role": "user", "content": f"{Query}"})
        
        print(f"🤖 Sending query to Groq: {Query}")
        
        # Call Groq API
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + groq_messages,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None
        )
        
        # Stream the response
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
                
        Answer = Answer.replace("</s>", "").strip()
        
        # FIXED: Save only role and content (no date/id)
        messages.append({"role": "assistant", "content": Answer})
        
        # FIXED: Save messages safely
        save_chatlog(messages)
        
        # Clean up the answer
        Answer = AnswerModifier(Answer)
        
        # Cache the response
        response_cache[cache_key] = {'answer': Answer, 'time': current_time}
        
        print(f"✅ Response generated: {Answer[:100]}...")
        return Answer
        
    except Exception as e:
        print(f"❌ ChatBot error: {e}")
        
        # Provide helpful error messages
        error_messages = {
            "rate limit": "🚫 API rate limit exceeded. Please try again in a moment.",
            "timeout": "⏰ Request timeout. Please check your internet connection.",
            "authentication": "🔐 Authentication failed. Please check your API key.",
            "connection": "🌐 Connection error. Please check your internet connection."
        }
        
        error_str = str(e).lower()
        for key, message in error_messages.items():
            if key in error_str:
                return f"{message}\n\n💡 *In the meantime, try commands like 'open youtube' or 'play music'*"
        
        return "❌ Sorry, I encountered an error processing your request. Please try again."
















# from groq import Groq
# from json import load, dump
# import datetime
# from dotenv import dotenv_values
# import time
# import pymongo
# import os

# env_vars = dotenv_values(".env")
# GroqAPIKey = env_vars.get("GroqAPIKey")
# MONGODB_URI = env_vars.get("MONGODB_URI")

# if not GroqAPIKey:
#     raise ValueError("GroqAPIKey is not set in .env file")

# client = Groq(api_key=GroqAPIKey)
# mongo_client = pymongo.MongoClient(MONGODB_URI)
# db = mongo_client['ai_assistant']
# users = db['users']

# messages = []
# response_cache = {}  # Cache for deduplication

# def RealtimeInformation():
#     current_date_time = datetime.datetime.now()
#     day = current_date_time.strftime("%A")
#     date = current_date_time.strftime("%d")
#     month = current_date_time.strftime("%B")
#     year = current_date_time.strftime("%Y")
#     hour = current_date_time.strftime("%H")
#     minute = current_date_time.strftime("%M")
#     second = current_date_time.strftime("%S")
    
#     data = f"Please use this real-time information if needed,\n"
#     data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
#     data += f"Hour: {hour}\nMinute: {minute}\nSecond: {second}\n"
#     return data

# def AnswerModifier(Answer):
#     lines = Answer.split("\n")
#     non_empty_lines = [line for line in lines if line.strip()]
#     modified_answer = "\n".join(non_empty_lines)
#     return modified_answer

# def ChatBot(Query, username, assistantname):
#     try:
#         # Check cache
#         cache_key = Query.lower().strip()
#         current_time = time.time()
#         if cache_key in response_cache and current_time - response_cache[cache_key]['time'] < 5:
#             print(f"Returning cached response for query: {Query}")
#             return response_cache[cache_key]['answer']

#         System = f"""Hello, I am {username}, You are a very accurate and advanced AI chatbot named {assistantname} which also has real-time up-to-date information from the internet.
# *** Do not tell time until I ask, do not talk too much, just answer the question.***
# *** Reply in only English, even if the question is in Hindi, reply in English.***
# *** Do not provide notes in the output, just answer the question and never mention your training data. ***
# """
#         SystemChatBot = [{"role": "system", "content": System}]

#         chatlog_path = r"Data/ChatLog.json"
#         try:
#             if os.path.exists(chatlog_path):
#                 with open(chatlog_path, "r", encoding="utf-8") as f:
#                     messages = load(f)
#             else:
#                 messages = []
#                 print(f"ChatLog.json not found, initializing empty messages")
#         except Exception as e:
#             print(f"Error reading ChatLog.json: {e}")
#             messages = []

#         # FIXED: Strip date and id for Groq API - ONLY keep role/content
#         groq_messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages if isinstance(msg, dict) and "role" in msg and "content" in msg]
#         groq_messages.append({"role": "user", "content": f"{Query}"})
        
#         print(f"Sending query to Groq: {Query}")
#         completion = client.chat.completions.create(
#             model="llama-3.3-70b-versatile",  # FIXED: Updated to non-deprecated model
#             messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + groq_messages,
#             temperature=0.7,
#             max_tokens=1024,
#             top_p=1,
#             stream=True,
#             stop=None
#         )
        
#         Answer = ""
#         for chunk in completion:
#             if chunk.choices[0].delta.content:
#                 Answer += chunk.choices[0].delta.content
#                 print(f"Received chunk: {chunk.choices[0].delta.content}")
                
#         Answer = Answer.replace("</s>", "")
#         # FIXED: Save ONLY role/content - NO DATE/ID
#         messages.append({"role": "assistant", "content": Answer})
        
#         try:
#             with open(chatlog_path, "w", encoding="utf-8") as f:
#                 dump(messages, f, indent=4)
#         except Exception as e:
#             print(f"Error writing to ChatLog.json: {e}")
            
#         Answer = AnswerModifier(Answer)
#         response_cache[cache_key] = {'answer': Answer, 'time': current_time}
#         print(f"Returning response: {Answer}")
#         return Answer
#     except Exception as e:
#         print(f"ChatBot error: {e}")
#         return "Sorry, I couldn't process that. Please try again."



#===============only backend ======================================#

# from groq import Groq
# from json import load, dump
# import datetime
# from dotenv import dotenv_values

# env_vars = dotenv_values(".env")

# Username = env_vars.get("Username")
# Assistantname = env_vars.get("Assistantname")
# GroqAPIKey = env_vars.get("GroqAPIKey")

# client = Groq(api_key=GroqAPIKey)

# messages = []

# System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
# *** Do not tell time until I ask, do not talk too much, just answer the question.***
# *** Reply in only English, even if the question is in Hindi, reply in English.***
# *** Do not provide notes in the output, just answer the question and never mention your training data. ***
# """

# SystemChatBot = [
#     {
#         "role": "system", "content": System
#     }
# ]

# try:
#     with open(r"Data/ChatLog.json", "r") as f:
#         messages = load(f)
# except FileNotFoundError:
#     with open(r"Data/ChatLog.json", "w") as f:
#         dump([],f)
        
# def RealtimeInformation():
#     current_date_time = datetime.datetime.now()
#     day = current_date_time.strftime("%A")
#     date = current_date_time.strftime("%d")
#     month = current_date_time.strftime("%B")
#     year = current_date_time.strftime("%Y")
#     hour = current_date_time.strftime("%H")
#     minute = current_date_time.strftime("%M")
#     second = current_date_time.strftime("%S")
    
#     data = f"Please use this real-time information if needed,\n"
#     data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
#     data += f"Hour: {hour}\nMinute: {minute}\nSecond: {second}\n"
#     return data

# def AnswerModifier(Answer):
#     lines = Answer.split("\n")
#     non_empty_lines = [line for line in lines if line.strip()]
#     modified_answer = "\n".join(non_empty_lines)
#     return modified_answer

# def ChatBot(Query):
#     """This function sends the user's query to the chatbot model and returns the AI's response."""
    
#     try:
#         with open(r"Data/ChatLog.json", "r") as f:
#             messages = load(f)
            
#             messages.append({"role": "user", "content": f"{Query}"})
            
#             completion = client.chat.completions.create(
#                 model="llama-3.3-70b-versatile",
#                 messages=SystemChatBot + [{"role": "system", "content":RealtimeInformation()}] + messages,
#                 temperature=0.7,
#                 max_tokens=1024,
#                 top_p=1,
#                 stream=True,
#                 stop=None
                
#             )
            
#             Answer = ""
            
#             for chunk in completion:
#                 if chunk.choices[0].delta.content:
#                     Answer += chunk.choices[0].delta.content
                    
#             Answer = Answer.replace("</s>", "")
#             messages.append({"role": "assistant", "content": Answer})
            
#             with open(r"Data/ChatLog.json", "w") as f:
#                 dump(messages, f, indent=4)
                
#             return AnswerModifier(Answer=Answer)
#     except Exception as e:
#         print(f"Error: {e}")
#         with open(r"Data/ChatLog.json", "w") as f:
#             dump([], f, indent=4)
#         return ChatBot(Query)
                    
# if __name__ == "__main__":
#     while True:
#         user_input = input("Enter Your Query: ")
#         print(ChatBot(user_input))            