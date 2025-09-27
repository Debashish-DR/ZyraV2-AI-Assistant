import os
import json
from groq import Groq
import datetime
from dotenv import dotenv_values
import requests
from bs4 import BeautifulSoup

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None

System = f"""You are {Assistantname}, an AI assistant with real-time information access. 
*** STRICT RULES: ***
1. NEVER use phrases like "Unfortunately", "I couldn't find", "I don't have information"
2. NEVER apologize or make disclaimers about your knowledge
3. ALWAYS answer directly and confidently using the provided search results
4. If search results exist, provide a clear factual answer
5. If no results exist, say "No information found" without extra words
6. Be concise and factual - no unnecessary words

User: {Username}. Provide direct answers only."""

# FIXED: Safe file reading with folder creation
def load_messages():
    try:
        os.makedirs("Data", exist_ok=True)
        chatlog_path = "Data/ChatLog.json"
        if os.path.exists(chatlog_path):
            with open(chatlog_path, "r") as f:
                return json.load(f)
        else:
            with open(chatlog_path, "w") as f:
                json.dump([], f)
            return []
    except Exception as e:
        print(f"Error loading messages: {e}")
        return []

# FIXED: Initialize messages safely
messages = load_messages()

def get_direct_answer(query):
    try:
        ddg_url = f"https://api.duckduckgo.com/?q={query.replace(' ', '+')}&format=json&no_html=1"
        response = requests.get(ddg_url, timeout=8)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('AbstractText') and data['AbstractText']:
                return data['AbstractText']
            
            if data.get('Answer') and data['Answer']:
                return data['Answer']
                
            if data.get('Definition') and data['Definition']:
                return data['Definition']
                
    except Exception as e:
        print(f"DuckDuckGo API error: {e}")
    
    return None
        
def DuckDuckGoSearch(Query):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        url = f"https://duckduckgo.com/html/?q={Query.replace(' ', '+')}"
        response = requests.get(url, headers=headers, timeout=8)
        
        if response.status_code != 200:
            return f"No search results found for: {Query}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('div', class_='result__body', limit=3)
        
        if not results:
            return f"No search results found for: {Query}"
        
        Answer = f"Search results for '{Query}':\n"
        for i, result in enumerate(results, 1):
            title = result.find('a', class_='result__a').text.strip() if result.find('a', class_='result__a') else "No title"
            description = result.find('a', class_='result__snippet').text.strip() if result.find('a', class_='result__snippet') else "No description"
            link = result.find('a', class_='result__url')['href'] if result.find('a', class_='result__url') else "No URL"
            Answer += f"\n{i}. {title}\n   {description}\n   URL: {link}\n"
        
        return Answer
    
    except Exception as e:
        return f"Search error: {str(e)}"

def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content":"Hi"},
    {"role": "assistant", "content":"Hello! How can I assist you?"} 
]

def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    
    data += f"Use This Real-time information if needed: \n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data

def RealtimeSearchEngine(prompt):
    global messages
    
    if client is None:
        return "Groq API not configured."
    
    direct_answer = get_direct_answer(prompt)
    if direct_answer:
        return direct_answer
    
    # FIXED: Load messages safely
    clean_messages = []
    for msg in messages:
        if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
            clean_msg = {"role": msg["role"], "content": msg["content"]}
            clean_messages.append(clean_msg)
    
    clean_messages.append({"role": "user", "content": prompt})
    
    search_data = DuckDuckGoSearch(prompt)
    SystemChatBot.append({"role": "system", "content": search_data})
    
    strict_instruction = {
        "role": "system", 
        "content": "IMPORTANT: Answer directly using the search data. Never say 'unfortunately' or 'I couldn't find'. Be confident and factual."
    }
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + [strict_instruction] + [{"role": "system", "content":Information()}] + clean_messages,
            temperature=0.1,
            max_tokens=500,
            top_p=1,
            stream=True,
            stop=None
        )
        
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
                
        Answer = Answer.strip().replace("</s>", "")
        
        vague_phrases = [
            "unfortunately", "i couldn't find", "i don't have", 
            "not in my knowledge", "may not be", "please check",
            "however, i can suggest", "as of my knowledge"
        ]
        
        for phrase in vague_phrases:
            if phrase in Answer.lower():
                Answer = Answer.lower().replace(phrase, "").capitalize()
        
        # FIXED: Save safely
        clean_messages.append({"role": "assistant", "content": Answer})
        
        try:
            with open("Data/ChatLog.json", "w") as f:
                json.dump(clean_messages, f, indent=4)
        except Exception as e:
            print(f"Error saving chatlog: {e}")
            
        SystemChatBot.pop()
        return AnswerModifier(Answer)
        
    except Exception as e:
        print(f"RealtimeSearchEngine error: {e}")
        if "Search results for" in search_data:
            return search_data
        return "Search service unavailable. Try again."




#================================================================================
# Realtime Search Engine using DuckDuckGo and Groq LLM
#================================================================================


# from googlesearch import search  # You can remove this if not needed anymore
# from groq import Groq
# from json import load, dump
# import datetime
# from dotenv import dotenv_values
# import requests
# from bs4 import BeautifulSoup

# env_vars = dotenv_values(".env")

# Username = env_vars.get("Username")
# Assistantname = env_vars.get("Assistantname")
# GroqAPIKey = env_vars.get("GroqAPIKey")

# client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None

# System = f"""You are {Assistantname}, an AI assistant with real-time information access. 
# *** STRICT RULES: ***
# 1. NEVER use phrases like "Unfortunately", "I couldn't find", "I don't have information"
# 2. NEVER apologize or make disclaimers about your knowledge
# 3. ALWAYS answer directly and confidently using the provided search results
# 4. If search results exist, provide a clear factual answer
# 5. If no results exist, say "No information found" without extra words
# 6. Be concise and factual - no unnecessary words

# User: {Username}. Provide direct answers only."""

# try:
#     with open(r"Data/ChatLog.json", "r") as f:
#         messages = load(f)
# except:
#     with open(r"Data/ChatLog.json", "w") as f:
#         dump([],f)

# def get_direct_answer(query):
#     """Use DuckDuckGo API for reliable direct answers"""
#     try:
#         # Use DuckDuckGo Instant Answer API (free and reliable)
#         ddg_url = f"https://api.duckduckgo.com/?q={query.replace(' ', '+')}&format=json&no_html=1"
#         response = requests.get(ddg_url, timeout=8)
        
#         if response.status_code == 200:
#             data = response.json()
            
#             # Return Abstract text if available
#             if data.get('AbstractText') and data['AbstractText']:
#                 return data['AbstractText']
            
#             # Return Answer if available
#             if data.get('Answer') and data['Answer']:
#                 return data['Answer']
                
#             # Return Definition if available
#             if data.get('Definition') and data['Definition']:
#                 return data['Definition']
                
#     except Exception as e:
#         print(f"DuckDuckGo API error: {e}")
    
#     return None
        
# def DuckDuckGoSearch(Query):
#     """Scrape DuckDuckGo for search results using requests and BeautifulSoup"""
#     try:
#         headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#         }
#         url = f"https://duckduckgo.com/html/?q={Query.replace(' ', '+')}"
#         response = requests.get(url, headers=headers, timeout=8)
        
#         if response.status_code != 200:
#             return f"No search results found for: {Query}"
        
#         soup = BeautifulSoup(response.text, 'html.parser')
#         results = soup.find_all('div', class_='result__body', limit=3)  # Top 3 results
        
#         if not results:
#             return f"No search results found for: {Query}"
        
#         Answer = f"Search results for '{Query}':\n"
#         for i, result in enumerate(results, 1):
#             title = result.find('a', class_='result__a').text.strip() if result.find('a', class_='result__a') else "No title"
#             description = result.find('a', class_='result__snippet').text.strip() if result.find('a', class_='result__snippet') else "No description"
#             link = result.find('a', class_='result__url')['href'] if result.find('a', class_='result__url') else "No URL"
#             Answer += f"\n{i}. {title}\n   {description}\n   URL: {link}\n"
        
#         return Answer
    
#     except Exception as e:
#         return f"Search error: {str(e)}"

# def AnswerModifier(Answer):
#     lines = Answer.split("\n")
#     non_empty_lines = [line for line in lines if line.strip()]
#     modified_answer = "\n".join(non_empty_lines)
#     return modified_answer

# SystemChatBot = [
#     {"role": "system", "content": System},
#     {"role": "user", "content":"Hi"},
#     {"role": "assistant", "content":"Hello! How can I assist you?"} 
# ]

# def Information():
#     data = ""
#     current_date_time = datetime.datetime.now()
#     day = current_date_time.strftime("%A")
#     date = current_date_time.strftime("%d")
#     month = current_date_time.strftime("%B")
#     year = current_date_time.strftime("%Y")
#     hour = current_date_time.strftime("%H")
#     minute = current_date_time.strftime("%M")
#     second = current_date_time.strftime("%S")
    
#     data += f"Use This Real-time information if needed: \n"
#     data += f"Day: {day}\n"
#     data += f"Date: {date}\n"
#     data += f"Month: {month}\n"
#     data += f"Year: {year}\n"
#     data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
#     return data

# def RealtimeSearchEngine(prompt):
#     global SystemChatBot, messages
    
#     if client is None:
#         return "Groq API not configured."
    
#     # FIRST: Try to get direct answer from DuckDuckGo API
#     direct_answer = get_direct_answer(prompt)
#     if direct_answer:
#         return direct_answer
    
#     # ONLY if no direct answer found, use AI processing
#     with open(r"Data/ChatLog.json", "r") as f:
#         messages = load(f)
        
#     messages.append({"role": "user", "content": prompt})
    
#     search_data = DuckDuckGoSearch(prompt)  # Replaced with new scraper function
#     SystemChatBot.append({"role": "system", "content": search_data})
    
#     # STRICT INSTRUCTION TO PREVENT VAGUE ANSWERS
#     strict_instruction = {
#         "role": "system", 
#         "content": "IMPORTANT: Answer directly using the search data. Never say 'unfortunately' or 'I couldn't find'. Be confident and factual."
#     }
    
#     try:
#         completion = client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=SystemChatBot + [strict_instruction] + [{"role": "system", "content":Information()}] + messages,
#             temperature=0.1,
#             max_tokens=500,
#             top_p=1,
#             stream=True,
#             stop=None
#         )
        
#         Answer = ""
#         for chunk in completion:
#             if chunk.choices[0].delta.content:
#                 Answer += chunk.choices[0].delta.content
                
#         Answer = Answer.strip().replace("</s>", "")
        
#         # STRICT FILTER: Remove any vague language
#         vague_phrases = [
#             "unfortunately", "i couldn't find", "i don't have", 
#             "not in my knowledge", "may not be", "please check",
#             "however, i can suggest", "as of my knowledge"
#         ]
        
#         for phrase in vague_phrases:
#             if phrase in Answer.lower():
#                 Answer = Answer.lower().replace(phrase, "").capitalize()
        
#         messages.append({"role": "assistant", "content": Answer})
        
#         with open(r"Data/ChatLog.json", "w") as f:
#             dump(messages, f, indent=4)
            
#         SystemChatBot.pop()
#         return AnswerModifier(Answer)
        
#     except Exception as e:
#         # If AI fails, try to return the direct answer from search data
#         if "Search results for" in search_data:
#             return search_data
#         return "Search service unavailable. Try again."

# if __name__ == "__main__":
#     while True:
#         prompt = input("Enter your query: ")
#         Answer = RealtimeSearchEngine(prompt)
#         print(Answer)    





#================================================================================
# Device Manager for Mobile/PC Detection and Connection Method





# from googlesearch import search
# from groq import Groq
# from json import load, dump
# import datetime
# from dotenv import dotenv_values

# env_vars = dotenv_values(".env")

# Username = env_vars.get("Username")
# Assistantname = env_vars.get("Assistantname")
# GroqAPIKey = env_vars.get("GroqAPIKey")

# client = Groq(api_key=GroqAPIKey)

# System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
# *** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
# *** Just answer the question from the provided data in a professional way. ***"""

# try:
#     with open(r"Data/ChatLog.json", "r") as f:
#         messages = load(f)
# except:
#     with open(r"Data/ChatLog.json", "w") as f:
#         dump([],f)
        
# def GoogleSearch(Query):
#     results = list(search(Query, advanced=True, num_results=5))
#     Answer = f"The search results for '{Query}' are: \n[start]\n"
    
#     for i in results:
#         Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
        
#     Answer += "[end]"
#     return Answer

# def AnswerModifier(Answer):
#     lines = Answer.split("\n")
#     non_empty_lines = [line for line in lines if line.strip()]
#     modified_answer = "\n".join(non_empty_lines)
#     return modified_answer

# SystemChatBot = [
#     {"role": "system", "content": System},
#     {"role": "user", "content":"Hi"},
#     {"role": "assistant", "content":"Hello! How can I assist you?"} 
# ]

# def Information():
#     data = ""
#     current_date_time = datetime.datetime.now()
#     day = current_date_time.strftime("%A")
#     date = current_date_time.strftime("%d")
#     month = current_date_time.strftime("%B")
#     year = current_date_time.strftime("%Y")
#     hour = current_date_time.strftime("%H")
#     minute = current_date_time.strftime("%M")
#     second = current_date_time.strftime("%S")
    
#     data += f"Use This Real-time information if needed: \n"
#     data += f"Day: {day}\n"
#     data += f"Date: {date}\n"
#     data += f"Month: {month}\n"
#     data += f"Year: {year}\n"
#     data += f"Time: {hour} hours, {minute} mintues, {second} seconds.\n"
#     return data

# def RealtimeSearchEngine(prompt):
#     global SystemChatBot, messages
    
#     with open(r"Data/ChatLog.json", "r") as f:
#         messages = load(f)
        
#     messages.append({"role": "user", "content": f"{prompt}"})
    
#     SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})
    
#     completion = client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         messages=SystemChatBot + [{"role": "system", "content":Information()}] + messages,
#         temperature=0.7,
#         max_tokens=2048,
#         top_p=1,
#         stream=True,
#         stop=None
#     )
    
#     Answer = ""
    
#     for chunk in completion:
#         if chunk.choices[0].delta.content:
#             Answer += chunk.choices[0].delta.content
            
#     Answer = Answer.strip().replace("</s>", "")
#     messages.append({"role": "assistant", "content": Answer})
    
#     with open(r"Data/ChatLog.json", "w") as f:
#         dump(messages, f, indent=4)
        
#     SystemChatBot.pop()
#     return AnswerModifier(Answer=Answer)

# if __name__ == "__main__":
#     while True:
#         prompt = input("Enter your query: ")
#         Answer = RealtimeSearchEngine(prompt)
#         print(Answer)
        