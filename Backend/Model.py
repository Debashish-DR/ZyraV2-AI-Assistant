import cohere
from groq import Groq
from dotenv import dotenv_values
import re

env_vars = dotenv_values(".env")
CohereAPIKey = env_vars.get("CohereAPIKey")
GroqAPIKey = env_vars.get("GroqAPIKey")

co = cohere.Client(api_key=CohereAPIKey) if CohereAPIKey else None
groq_client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None

tools = [
    {
        "name": "general_conversation",
        "description": "THIS IS THE DEFAULT TOOL. Use this for ANY conversational query, greeting, farewell, philosophical question, or if the user's intent is unclear. This includes 'hello', 'how are you', 'what is your name', 'who are you', 'thanks', 'bye', and any question that does not explicitly require a real-time search or a specific action like opening an app.",
        "parameter_definitions": {
            "query": {
                "description": "The user's original query.",
                "type": "str",
                "required": True
            }
        }
    },
    {
        "name": "realtime_information",
        "description": "Get real-time, up-to-date information. Use for news, current events, weather, or facts about people/companies that change often.",
        "parameter_definitions": {
            "query": {
                "description": "The search query for real-time information.",
                "type": "str",
                "required": True
            }
        }
    },
    {
        "name": "automation_task",
        "description": "Control computer applications or perform system actions.",
        "parameter_definitions": {
            "action": {
                "description": "The action to perform. Must be: 'open', 'close', 'mute', 'unmute', 'volume_up', 'volume_down', 'lock', 'shutdown', 'close_all_tabs', 'close_all_windows'.",
                "type": "str",
                "required": True
            },
            "target": {
                "description": "The target of the action. For 'open'/'close', it's the app name (e.g., 'chrome', 'notepad'). For volume, it can be a number like '50'. Empty for 'close_all_tabs' or 'close_all_windows'.",
                "type": "str",
                "required": False
            }
        }
    },
    {
        "name": "media_control",
        "description": "Control media playback. Play a specific song or control playback (play, pause, next, previous).",
        "parameter_definitions": {
            "action": {
                "description": "The action to perform. Must be: 'play', 'pause', 'next', 'previous', 'stop'.",
                "type": "str",
                "required": True
            },
            "query": {
                "description": "The name of the song or artist to play. Only needed if action is 'play'.",
                "type": "str",
                "required": False
            }
        }
    },
    {
        "name": "generate_image",
        "description": "Generate an image from a text description.",
        "parameter_definitions": {
            "prompt": {
                "description": "The detailed description of the image to generate.",
                "type": "str",
                "required": True
            }
        }
    },
    {
        "name": "set_reminder",
        "description": "Create a new reminder with a time and message.",
        "parameter_definitions": {
            "message": {
                "description": "The reminder message.",
                "type": "str",
                "required": True
            },
            "time": {
                "description": "The time for the reminder (e.g., '5:00 pm', 'in 20 minutes').",
                "type": "str",
                "required": True
            }
        }
    },
    {
        "name": "web_search",
        "description": "Perform a web search on Google or YouTube.",
        "parameter_definitions": {
            "engine": {
                "description": "The search engine to use. Must be: 'google' or 'youtube'.",
                "type": "str",
                "required": True
            },
            "query": {
                "description": "The term to search for.",
                "type": "str",
                "required": True
            }
        }
    },
    {
        "name": "phone_control",
        "description": "Make a phone call or send a message to a contact.",
        "parameter_definitions": {
            "action": {
                "description": "The action to perform. Must be: 'call', 'message'.",
                "type": "str",
                "required": True
            },
            "contact": {
                "description": "The name of the contact to call or message.",
                "type": "str",
                "required": True
            },
            "message": {
                "description": "The message to send. Required only if action is 'message'.",
                "type": "str",
                "required": False
            }
        }
    },
    {
        "name": "exit_assistant",
        "description": "Shut down the voice assistant.",
        "parameter_definitions": {}
    }
]

preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', etc.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
-> Respond with 'system close all tabs' if a query is asking to close all browser tabs like 'close all tabs' or 'close all browser tabs'.
-> Respond with 'system close all windows' if a query is asking to close all open windows or applications like 'close all windows' or 'close all applications'.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc. but if the query is asking to play multiple songs, respond with 'play 1st song name, play 2nd song name' and so on.
-> Respond with 'system pause' if a query is asking to pause media playback like 'pause music', 'pause video', 'pause the song', etc.
-> Respond with 'system resume' if a query is asking to resume media playback like 'resume music', 'continue playing', 'play again', etc.
-> Respond with 'system next' if a query is asking to play next media like 'next song', 'next track', 'skip this', etc.
-> Respond with 'system previous' if a query is asking to play previous media like 'previous song', 'go back', 'last track', etc.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting'.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down, lock, shutdown, etc. but if the query is asking to do multiple tasks, respond with 'system 1st task, system 2nd task', etc.
-> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic but if the query is asking to write multiple types of content, respond with 'content 1st topic, content 2nd topic' and so on.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube but if the query is asking to search multiple topics on youtube, respond with 'youtube search 1st topic, youtube search 2nd topic' and so on.
*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
*** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""

def FirstLayerDMM(prompt: str = "test"):
    if not prompt or not isinstance(prompt, str) or prompt.strip() == "":
        return ["general I didn't catch that. Could you please repeat?"]
    
    if co is not None:
        try:
            response = co.chat(
                model='command-r-plus',
                message=prompt,
                temperature=0.1,
                tools=tools,
            )

            results = []
            if response.tool_calls:
                for tool in response.tool_calls:
                    if tool.name == "general_conversation":
                        results.append(f"general {tool.parameters['query']}")
                    elif tool.name == "realtime_information":
                        results.append(f"realtime {tool.parameters['query']}")
                    elif tool.name == "automation_task":
                        action = tool.parameters['action']
                        target = tool.parameters.get('target', '')
                        if action in ['open', 'close']:
                            results.append(f"{action} {target}")
                        elif action in ['mute', 'unmute', 'volume_up', 'volume_down', 'lock', 'shutdown', 'close_all_tabs', 'close_all_windows']:
                            results.append(f"system {action}")
                    elif tool.name == "media_control":
                        action = tool.parameters['action']
                        query = tool.parameters.get('query', '')
                        if action == 'play' and query:
                            results.append(f"play {query}")
                        else:
                            results.append(f"system {action}")
                    elif tool.name == "generate_image":
                        results.append(f"generate image {tool.parameters['prompt']}")
                    elif tool.name == "set_reminder":
                        msg = tool.parameters['message']
                        time = tool.parameters['time']
                        results.append(f"reminder {time} {msg}")
                    elif tool.name == "web_search":
                        engine = tool.parameters['engine']
                        query = tool.parameters['query']
                        results.append(f"{engine} search {query}")
                    elif tool.name == "phone_control":
                        action = tool.parameters['action']
                        contact = tool.parameters['contact']
                        if action == 'call':
                            results.append(f"call {contact}")
                        elif action == 'message':
                            message = tool.parameters.get('message', '')
                            results.append(f"message {contact} {message}")
                    elif tool.name == "exit_assistant":
                        results.append("exit")

            if results:
                return results
            else:
                return ["general " + prompt]

        except Exception as e:
            if groq_client is not None:
                return groq_fallback(prompt)
            else:
                return enhanced_fallback_decision_making(prompt)
    
    elif groq_client is not None:
        return groq_fallback(prompt)
    
    else:
        return enhanced_fallback_decision_making(prompt)

def groq_fallback(prompt: str):
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": preamble}, {"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=100
        )
        decision_text = completion.choices[0].message.content.strip()
        
        decisions = [d.strip() for d in decision_text.split(',')]
        results = []
        for d in decisions:
            if 'realtime (' in d:
                results.append(d.replace('realtime (', 'realtime ').replace(')', ''))
            elif 'general (' in d:
                results.append(d.replace('general (', 'general ').replace(')', ''))
            elif d.startswith(('open ', 'close ', 'play ', 'generate image ', 'reminder ', 'system ', 'google search ', 'youtube search ', 'call ', 'message ', 'content ')) or d == 'exit':
                results.append(d)
            else:
                results.append(f"general {prompt}")
        
        return results if results else ["general " + prompt]
    
    except Exception as e:
        return enhanced_fallback_decision_making(prompt)

def fallback_decision_making(prompt: str):
    prompt_lower = prompt.lower().strip()
    
    # FIXED: Better media control detection
    media_controls = {
        "pause": "pause",
        "stop": "pause", 
        "resume": "resume",
        "continue": "resume",
        "next": "next",
        "skip": "next",
        "previous": "previous",
        "back": "previous"
    }
    
    for word, action in media_controls.items():
        if word in prompt_lower and any(media_word in prompt_lower for media_word in ["music", "song", "video", "media", "playback"]):
            return [f"system {action}"]
    
    if any(word in prompt_lower for word in ["play", "music", "song"]):
        if "believer" in prompt_lower:
            return ["play Believer Imagine Dragons"]
        elif "spotify" in prompt_lower:
            return ["play on spotify"]
        else:
            return ["play music"]
    
    elif any(word in prompt_lower for word in ["volume", "sound", "mute"]):
        if "mute" in prompt_lower:
            return ["system mute"]
        elif "up" in prompt_lower:
            return ["system volume_up"]
        elif "down" in prompt_lower:
            return ["system volume_down"]
        else:
            return ["system volume 50"]
    
    elif any(word in prompt_lower for word in ["open", "start", "launch"]):
        if "chrome" in prompt_lower:
            return ["open chrome"]
        elif "youtube" in prompt_lower:
            return ["open youtube"]
        elif "music" in prompt_lower:
            return ["open youtube music"]
    
    elif any(word in prompt_lower for word in ["exit", "quit", "bye", "goodbye"]):
        return ["exit"]
    
    return ["general " + prompt]

def enhanced_fallback_decision_making(prompt: str):
    prompt_lower = prompt.lower().strip()
    
    if "close all tabs" in prompt_lower or "close all browser tabs" in prompt_lower:
        return ["system close all tabs"]
    elif "close all windows" in prompt_lower or "close all applications" in prompt_lower:
        return ["system close all windows"]
    
    realtime_keywords = ['who is ', 'current ', 'today\'s ', 'recent ', 'news ', 'update ', 'prime minister', 'president', 'weather', 'stock']
    if any(kw in prompt_lower for kw in realtime_keywords) or re.search(r'who is [a-zA-Z\s]+', prompt_lower):
        return [f"realtime {prompt}"]
    
    time_keywords = ['time', 'date', 'day', 'month', 'year']
    if any(word in prompt_lower for word in time_keywords):
        return [f"general {prompt}"]
    
    return fallback_decision_making(prompt)






#=========================================initial==================================================

# import cohere
# from groq import Groq
# from rich import print
# from dotenv import dotenv_values
# import re

# env_vars = dotenv_values(".env")
# CohereAPIKey = env_vars.get("CohereAPIKey")
# GroqAPIKey = env_vars.get("GroqAPIKey")

# # Initialize clients
# co = cohere.Client(api_key=CohereAPIKey) if CohereAPIKey else None
# groq_client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None

# if not CohereAPIKey:
#     print("[WARNING] Cohere API key not found. Using Groq fallback if available.")

# # List of functions for the old system (compatibility)
# funcs = [
#     "exit", "general", "realtime", "open", "close", "play", "generate image", "system", "content", "google search", "youtube search", "reminder", "call", "message"
# ]

# # --- NEW: Advanced Tool Definitions for Cohere ---
# tools = [
#     {
#         "name": "general_conversation",
#         "description": "THIS IS THE DEFAULT TOOL. Use this for ANY conversational query, greeting, farewell, philosophical question, or if the user's intent is unclear. This includes 'hello', 'how are you', 'what is your name', 'who are you', 'thanks', 'bye', and any question that does not explicitly require a real-time search or a specific action like opening an app.",
#         "parameter_definitions": {
#             "query": {
#                 "description": "The user's original query.",
#                 "type": "str",
#                 "required": True
#             }
#         }
#     },
#     {
#         "name": "realtime_information",
#         "description": "Get real-time, up-to-date information. Use for news, current events, weather, or facts about people/companies that change often.",
#         "parameter_definitions": {
#             "query": {
#                 "description": "The search query for real-time information.",
#                 "type": "str",
#                 "required": True
#             }
#         }
#     },
#     {
#         "name": "automation_task",
#         "description": "Control computer applications or perform system actions.",
#         "parameter_definitions": {
#             "action": {
#                 "description": "The action to perform. Must be: 'open', 'close', 'mute', 'unmute', 'volume_up', 'volume_down', 'lock', 'shutdown', 'close_all_tabs', 'close_all_windows'.",
#                 "type": "str",
#                 "required": True
#             },
#             "target": {
#                 "description": "The target of the action. For 'open'/'close', it's the app name (e.g., 'chrome', 'notepad'). For volume, it can be a number like '50'. Empty for 'close_all_tabs' or 'close_all_windows'.",
#                 "type": "str",
#                 "required": False
#             }
#         }
#     },
#     {
#         "name": "media_control",
#         "description": "Control media playback. Play a specific song or control playback (play, pause, next, previous).",
#         "parameter_definitions": {
#             "action": {
#                 "description": "The action to perform. Must be: 'play', 'pause', 'next', 'previous'.",
#                 "type": "str",
#                 "required": True
#             },
#             "query": {
#                 "description": "The name of the song or artist to play. Only needed if action is 'play'.",
#                 "type": "str",
#                 "required": False
#             }
#         }
#     },
#     {
#         "name": "generate_image",
#         "description": "Generate an image from a text description.",
#         "parameter_definitions": {
#             "prompt": {
#                 "description": "The detailed description of the image to generate.",
#                 "type": "str",
#                 "required": True
#             }
#         }
#     },
#     {
#         "name": "set_reminder",
#         "description": "Create a new reminder with a time and message.",
#         "parameter_definitions": {
#             "message": {
#                 "description": "The reminder message.",
#                 "type": "str",
#                 "required": True
#             },
#             "time": {
#                 "description": "The time for the reminder (e.g., '5:00 pm', 'in 20 minutes').",
#                 "type": "str",
#                 "required": True
#             }
#         }
#     },
#     {
#         "name": "web_search",
#         "description": "Perform a web search on Google or YouTube.",
#         "parameter_definitions": {
#             "engine": {
#                 "description": "The search engine to use. Must be: 'google' or 'youtube'.",
#                 "type": "str",
#                 "required": True
#             },
#             "query": {
#                 "description": "The term to search for.",
#                 "type": "str",
#                 "required": True
#             }
#         }
#     },
#     {
#         "name": "phone_control",
#         "description": "Make a phone call or send a message to a contact.",
#         "parameter_definitions": {
#             "action": {
#                 "description": "The action to perform. Must be: 'call', 'message'.",
#                 "type": "str",
#                 "required": True
#             },
#             "contact": {
#                 "description": "The name of the contact to call or message.",
#                 "type": "str",
#                 "required": True
#             },
#             "message": {
#                 "description": "The message to send. Required only if action is 'message'.",
#                 "type": "str",
#                 "required": False
#             }
#         }
#     },
#     {
#         "name": "exit_assistant",
#         "description": "Shut down the voice assistant.",
#         "parameter_definitions": {}
#     }
# ]

# preamble = """
# You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
# You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
# *** Do not answer any query, just decide what kind of query is given to you. ***
# -> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
# -> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', etc.
# -> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
# -> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
# -> Respond with 'system close all tabs' if a query is asking to close all browser tabs like 'close all tabs' or 'close all browser tabs'.
# -> Respond with 'system close all windows' if a query is asking to close all open windows or applications like 'close all windows' or 'close all applications'.
# -> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc. but if the query is asking to play multiple songs, respond with 'play 1st song name, play 2nd song name' and so on.
# -> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
# -> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting'.
# -> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down, lock, shutdown, etc. but if the query is asking to do multiple tasks, respond with 'system 1st task, system 2nd task', etc.
# -> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic but if the query is asking to write multiple types of content, respond with 'content 1st topic, content 2nd topic' and so on.
# -> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
# -> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube but if the query is asking to search multiple topics on youtube, respond with 'youtube search 1st topic, youtube search 2nd topic' and so on.
# *** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
# *** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
# *** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
# """

# chatHistory = [
#     {"role": "User", "message": "how are you?"},
#     {"role": "Chatbot", "message": "general how are you?"},
#     {"role": "User", "message": "do you like pizza?"},
#     {"role": "Chatbot", "message": "general do you like pizza?"},
#     {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
#     {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
#     {"role": "User", "message": "open chrome and firefox"},
#     {"role": "Chatbot", "message": "open chrome, open firefox"},
#     {"role": "User", "message": "what is today's date and by the way remind me that i have a dancing performance on 5th aug, reminder 11:00pm 5th aug dancing performance"},
#     {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
#     {"role": "User", "message": "chat with me."},
#     {"role": "Chatbot", "message": "general chat with me."}
# ]

# def FirstLayerDMM(prompt: str = "test"):
#     """
#     DECISION MAKING FUNCTION (UPGRADED)
#     Now uses Cohere's advanced Tool Use API for much more accurate decisions.
#     Falls back to Groq if Cohere unavailable, then to enhanced keyword rules.
#     Returns a list of strings in the OLD FORMAT for compatibility with your other files.
#     Example: ['open chrome', 'general who was gandhi?']
#     """
    
#     # Check if prompt is empty or invalid FIRST
#     if not prompt or not isinstance(prompt, str) or prompt.strip() == "":
#         print("[ERROR] Empty or invalid prompt received")
#         return ["general I didn't catch that. Could you please repeat?"]
    
#     # Try Cohere first
#     if co is not None:
#         try:
#             response = co.chat(
#                 model='command-r-plus',
#                 message=prompt,
#                 temperature=0.1,  # Low temperature for very precise decisions
#                 tools=tools,
#             )

#             results = []
#             if response.tool_calls:
#                 for tool in response.tool_calls:
#                     # Convert the advanced tool call back to the old string format your other files understand.
#                     if tool.name == "general_conversation":
#                         results.append(f"general {tool.parameters['query']}")
#                     elif tool.name == "realtime_information":
#                         results.append(f"realtime {tool.parameters['query']}")
#                     elif tool.name == "automation_task":
#                         action = tool.parameters['action']
#                         target = tool.parameters.get('target', '')
#                         if action in ['open', 'close']:
#                             results.append(f"{action} {target}")
#                         elif action in ['mute', 'unmute', 'volume_up', 'volume_down', 'lock', 'shutdown', 'close_all_tabs', 'close_all_windows']:
#                             results.append(f"system {action}")
#                     elif tool.name == "media_control":
#                         action = tool.parameters['action']
#                         query = tool.parameters.get('query', '')
#                         if action == 'play':
#                             results.append(f"play {query}")
#                         else:
#                             results.append(f"system {action}")
#                     elif tool.name == "generate_image":
#                         results.append(f"generate image {tool.parameters['prompt']}")
#                     elif tool.name == "set_reminder":
#                         msg = tool.parameters['message']
#                         time = tool.parameters['time']
#                         results.append(f"reminder {time} {msg}")
#                     elif tool.name == "web_search":
#                         engine = tool.parameters['engine']
#                         query = tool.parameters['query']
#                         results.append(f"{engine} search {query}")
#                     elif tool.name == "phone_control":
#                         action = tool.parameters['action']
#                         contact = tool.parameters['contact']
#                         if action == 'call':
#                             results.append(f"call {contact}")
#                         elif action == 'message':
#                             message = tool.parameters.get('message', '')
#                             results.append(f"message {contact} {message}")
#                     elif tool.name == "exit_assistant":
#                         results.append("exit")

#             if results:
#                 print(f"[Model Decision] {results}")
#                 return results
#             else:
#                 # If no tool call, default to general
#                 return ["general " + prompt]

#         except Exception as e:
#             print(f"[ERROR] Cohere API Error: {e}. Trying Groq fallback.")
#             if groq_client is not None:
#                 return groq_fallback(prompt)
#             else:
#                 return enhanced_fallback_decision_making(prompt)
    
#     # If no Cohere, try Groq
#     elif groq_client is not None:
#         print("[INFO] Using Groq for decision making.")
#         return groq_fallback(prompt)
    
#     # Final fallback
#     else:
#         print("[ERROR] No API available. Using enhanced fallback.")
#         return enhanced_fallback_decision_making(prompt)

# def groq_fallback(prompt: str):
#     """Use Groq to simulate tool decision based on preamble."""
#     try:
#         completion = groq_client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "system", "content": preamble}, {"role": "user", "content": prompt}],
#             temperature=0.1,
#             max_tokens=100
#         )
#         decision_text = completion.choices[0].message.content.strip()
        
#         # Parse the response (e.g., "realtime who is tony stark" → ['realtime who is tony stark'])
#         # Split by commas for multi-tasks
#         decisions = [d.strip() for d in decision_text.split(',')]
#         results = []
#         for d in decisions:
#             if 'realtime (' in d:
#                 results.append(d.replace('realtime (', 'realtime ').replace(')', ''))
#             elif 'general (' in d:
#                 results.append(d.replace('general (', 'general ').replace(')', ''))
#             elif d.startswith(('open ', 'close ', 'play ', 'generate image ', 'reminder ', 'system ', 'google search ', 'youtube search ', 'call ', 'message ', 'content ')) or d == 'exit':
#                 results.append(d)
#             else:
#                 results.append(f"general {prompt}")
        
#         print(f"[Groq Decision] {results}")
#         return results if results else ["general " + prompt]
    
#     except Exception as e:
#         print(f"[ERROR] Groq fallback failed: {e}")
#         return enhanced_fallback_decision_making(prompt)

# def fallback_decision_making(prompt: str):
#     """Fallback decision making when Cohere API fails"""
#     prompt_lower = prompt.lower().strip()
    
#     # Simple command detection as fallback
#     if any(word in prompt_lower for word in ["play", "music", "song"]):
#         if "believer" in prompt_lower:
#             return ["play Believer Imagine Dragons"]
#         elif "spotify" in prompt_lower:
#             return ["play on spotify"]
#         else:
#             return ["play music"]
    
#     elif any(word in prompt_lower for word in ["volume", "sound", "mute"]):
#         if "mute" in prompt_lower:
#             return ["system mute"]
#         elif "up" in prompt_lower:
#             return ["system volume up"]
#         elif "down" in prompt_lower:
#             return ["system volume down"]
#         else:
#             return ["system volume 50"]
    
#     elif any(word in prompt_lower for word in ["open", "start", "launch"]):
#         if "chrome" in prompt_lower:
#             return ["open chrome"]
#         elif "youtube" in prompt_lower:
#             return ["open youtube"]
#         elif "music" in prompt_lower:
#             return ["open youtube music"]
#         # Add more app detection here
    
#     elif any(word in prompt_lower for word in ["pause", "stop"]):
#         return ["system pause"]
    
#     elif any(word in prompt_lower for word in ["resume", "continue", "play"]):
#         return ["system resume"]
    
#     elif any(word in prompt_lower for word in ["exit", "quit", "bye", "goodbye"]):
#         return ["exit"]
    
#     # Default to general conversation
#     return ["general " + prompt]

# def enhanced_fallback_decision_making(prompt: str):
#     """Enhanced fallback with better realtime/general detection using regex/keywords."""
#     prompt_lower = prompt.lower().strip()
    
#     # Handle close all tabs/windows
#     if "close all tabs" in prompt_lower or "close all browser tabs" in prompt_lower:
#         return ["system close all tabs"]
#     elif "close all windows" in prompt_lower or "close all applications" in prompt_lower:
#         return ["system close all windows"]
    
#     # Realtime detection: Proper nouns, current events, news, individuals, time-sensitive
#     realtime_keywords = ['who is ', 'current ', 'today\'s ', 'recent ', 'news ', 'update ', 'prime minister', 'president', 'weather', 'stock']
#     if any(kw in prompt_lower for kw in realtime_keywords) or re.search(r'who is [a-zA-Z\s]+', prompt_lower):
#         return [f"realtime {prompt}"]
    
#     # Time/date to general
#     time_keywords = ['time', 'date', 'day', 'month', 'year']
#     if any(word in prompt_lower for word in time_keywords):
#         return [f"general {prompt}"]
    
#     # Rest as original fallback...
#     return fallback_decision_making(prompt)

# if __name__ == "__main__":
#     while True:
#         user_input = input(">>> ")
#         if user_input.lower() in ['exit', 'quit']:
#             break
#         result = FirstLayerDMM(user_input)
#         print(result)








#==========================================final==================================================
