from random import randint
from PIL import Image
import requests
from dotenv import dotenv_values
import os
import json
import sys

# Debug print function to ensure output to stdout
def debug_print(message):
    print(f"{message}", flush=True)

# Check if running on Render
IS_RENDER = os.environ.get('RENDER') is not None

# Ensure Data folder exists
def setup_data_folder():
    try:
        os.makedirs("Data", exist_ok=True)
        debug_print("[Backend Data folder is ready] <---- MODEL READY ---->")
    except Exception as e:
        debug_print(f"Error creating Data folder: {str(e)}")
        # Don't exit on folder creation error, just continue

setup_data_folder()

# Function to open and display images based on a given prompt
def get_images(prompt):
    debug_print(f"Getting images for prompt: {prompt}")
    folder_path = "Data"
    prompt = prompt.replace(" ", "_")
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]
    image_paths = []

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)
        if os.path.exists(image_path):
            image_paths.append(image_path)

    return image_paths

# Improved API key loading for both local and cloud environments
def get_api_key():
    # Priority 1: System environment variables (for Render.com)
    api_key = os.environ.get('HuggingFaceAPIKey')
    
    # Priority 2: .env file (for local development)
    if not api_key:
        try:
            env_vars = dotenv_values(".env")
            api_key = env_vars.get("HuggingFaceAPIKey")
        except:
            pass
    
    return api_key

# API details for the Hugging Face Stable Diffusion model
api_key = get_api_key()

if not api_key:
    debug_print("⚠️ HuggingFaceAPIKey not found - image generation disabled")
    debug_print("💡 To enable image generation, set HuggingFaceAPIKey in Render environment variables")
    # Don't exit - just disable image generation functionality
    headers = None
    API_URL = None
else:
    debug_print("✅ HuggingFaceAPIKey loaded successfully")
    headers = {"Authorization": f"Bearer {api_key}"}
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

def query(payload):
    # Check if API is configured
    if not api_key or not headers or not API_URL:
        debug_print("🔒 Image generation disabled - API key not configured")
        return None
        
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        debug_print(f"API response status: {response.status_code}")
        
        if response.status_code == 402:
            debug_print("API Error: Payment required (402). Add payment method to Hugging Face account.")
            return None
        if response.status_code != 200:
            debug_print(f"API Error: Status {response.status_code}")
            # Don't exit, just return None
            return None

        try:
            data = response.json()
            if "error" in data:
                debug_print(f"API Error: {data['error']}")
                return None
        except json.JSONDecodeError:
            return response.content

    except requests.Timeout:
        debug_print("API Error: Request timed out after 60 seconds")
        return None
    except Exception as e:
        debug_print(f"API Error: {str(e)}")
        return None

def generate_images(prompt: str):
    # Check if API is configured
    if not api_key:
        debug_print("🔒 Image generation disabled - no API key configured")
        return []
        
    debug_print(f"Generating images for prompt: {prompt}")
    image_bytes_list = []
    
    # Generate only 2 images on cloud to save resources
    num_images = 2 if IS_RENDER else 4
    
    for _ in range(num_images):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}"
        }
        image_bytes = query(payload)
        if image_bytes:
            image_bytes_list.append(image_bytes)
        else:
            debug_print("Skipping image due to API error")

    saved_images = []
    prompt_clean = prompt.replace(" ", "_").replace("/", "_")  # Sanitize filename

    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            try:
                image_path = f"Data/{prompt_clean}{i + 1}.jpg"
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
                saved_images.append(image_path)
                debug_print(f"✅ Saved image: {image_path}")
            except Exception as e:
                debug_print(f"❌ Error saving image {i + 1}: {str(e)}")
        else:
            debug_print(f"❌ No image data received for image {i + 1}")

    return saved_images

def GenerateImages(prompt: str):
    prompt = prompt.replace("generate image", "").strip()
    if not prompt:
        debug_print("❌ Error: No valid prompt provided")
        return []
    
    # Check if API is configured
    if not api_key:
        error_message = "🔒 **Image Generation Notice**\n\n"
        error_message += "🌐 *Image generation requires HuggingFace API key setup*\n"
        error_message += "💡 *To enable this feature:*\n"
        error_message += "1. Add 'HuggingFaceAPIKey' to Render environment variables\n"
        error_message += "2. Your app will automatically enable image generation!\n\n"
        error_message += "✅ *All other AI features work without this key*"
        
        # Return a placeholder image path or informative message
        placeholder_path = "Data/image_generation_disabled.txt"
        try:
            os.makedirs("Data", exist_ok=True)
            with open(placeholder_path, "w") as f:
                f.write(error_message)
            return [placeholder_path]
        except:
            return []
    
    try:
        saved = generate_images(prompt)
        if not saved:
            debug_print("❌ No images were generated successfully")
            error_message = "🖼️ **Image Generation Result**\n\n"
            error_message += "❌ *No images were generated for your prompt*\n"
            error_message += "💡 *Possible reasons:*\n"
            error_message += "- API service temporarily unavailable\n"
            error_message += "- Prompt may need more detail\n"
            error_message += "- Try again in a few moments\n\n"
            error_message += f"*Your prompt:* {prompt}"
            
            placeholder_path = "Data/image_generation_failed.txt"
            try:
                with open(placeholder_path, "w") as f:
                    f.write(error_message)
                return [placeholder_path]
            except:
                return []
        
        return saved
    except Exception as e:
        debug_print(f"❌ Error generating images for '{prompt}': {str(e)}")
        
        error_message = "🖼️ **Image Generation Error**\n\n"
        error_message += "❌ *Failed to generate images*\n"
        error_message += "💡 *This might be a temporary issue*\n"
        error_message += "- Please try again in a few moments\n"
        error_message += "- Or try a different prompt\n\n"
        error_message += f"*Your prompt:* {prompt}"
        
        placeholder_path = "Data/image_generation_error.txt"
        try:
            with open(placeholder_path, "w") as f:
                f.write(error_message)
            return [placeholder_path]
        except:
            return []








# from random import randint
# from PIL import Image
# import requests
# from dotenv import get_key
# import os
# import json
# import sys

# # Debug print function to ensure output to stdout
# def debug_print(message):
#     print(f"{message}", flush=True)

# # Ensure Data folder exists
# def setup_data_folder():
#     try:
#         os.makedirs("Data", exist_ok=True)
#         debug_print("[Backend Data folder is ready] <---- MODEL READY ---->")
#     except Exception as e:
#         debug_print(f"Error creating Data folder: {str(e)}")
#         sys.exit(1)

# setup_data_folder()

# # Function to open and display images based on a given prompt
# def get_images(prompt):
#     debug_print(f"Getting images for prompt: {prompt}")
#     folder_path = r"Data"
#     prompt = prompt.replace(" ", "_")
#     Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]
#     image_paths = []

#     for jpg_file in Files:
#         image_path = os.path.join(folder_path, jpg_file)
#         if os.path.exists(image_path):
#             image_paths.append(image_path)

#     return image_paths

# # API details for the Hugging Face Stable Diffusion model
# api_key = get_key('.env', 'HuggingFaceAPIKey')
# if not api_key:
#     debug_print("Error: HuggingFaceAPIKey not found in .env")
#     sys.exit(1)
# headers = {"Authorization": f"Bearer {api_key}"}
# API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

# def query(payload):
#     try:
#         response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
#         debug_print(f"API response status: {response.status_code}")
#         if response.status_code == 402:
#             debug_print("API Error: Payment required (402). Add payment method to Hugging Face account.")
#             return None
#         if response.status_code != 200:
#             debug_print(f"API Error: Status {response.status_code}")
#             return None

#         try:
#             data = response.json()
#             if "error" in data:
#                 debug_print(f"API Error: {data['error']}")
#                 return None
#         except json.JSONDecodeError:
#             return response.content

#     except requests.Timeout:
#         debug_print("API Error: Request timed out after 60 seconds")
#         return None
#     except Exception as e:
#         debug_print(f"API Error: {str(e)}")
#         return None

# def generate_images(prompt: str):
#     debug_print(f"Generating images for prompt: {prompt}")
#     tasks = []
#     image_bytes_list = []
#     for _ in range(4):
#         payload = {
#             "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}"
#         }
#         image_bytes = query(payload)
#         image_bytes_list.append(image_bytes)

#     saved_images = []
#     prompt_clean = prompt.replace(" ", "_")

#     for i, image_bytes in enumerate(image_bytes_list):
#         if image_bytes:
#             try:
#                 image_path = f"Data/{prompt_clean}{i + 1}.jpg"
#                 with open(image_path, "wb") as f:
#                     f.write(image_bytes)
#                 saved_images.append(image_path)
#                 debug_print(f"Saved image: {image_path}")
#             except Exception as e:
#                 debug_print(f"Error saving image {i + 1}: {str(e)}")

#     return saved_images

# def GenerateImages(prompt: str):
#     prompt = prompt.replace("generate image", "").strip()
#     if not prompt:
#         debug_print("Error: No valid prompt provided")
#         return []
#     try:
#         saved = generate_images(prompt)
#         return saved
#     except Exception as e:
#         debug_print(f"Error generating images for '{prompt}': {str(e)}")
#         return []






#============================ Original code commented out for reference============================================

# import asyncio
# from random import randint
# from PIL import Image
# import requests
# from dotenv import get_key
# import os
# import json
# import sys

# # Debug print function to ensure output to stdout
# def debug_print(message):
#     print(f"[ImageGeneration DEBUG] {message}", flush=True)

# # Ensure Data folder exists
# debug_print("Checking/creating Data folder...")
# try:
#     os.makedirs("Data", exist_ok=True)
#     debug_print("Data folder ready")
# except Exception as e:
#     debug_print(f"Error creating Data folder: {str(e)}")
#     print(f"Failed: {str(e)}", flush=True)
#     sys.exit(1)

# # Function to open and display images based on a given prompt
# def open_images(prompt):
#     debug_print(f"Opening images for prompt: {prompt}")
#     folder_path = r"Data"
#     prompt = prompt.replace(" ", "_")  # Replace spaces with underscores
#     Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]
#     opened = 0

#     for jpg_file in Files:
#         image_path = os.path.join(folder_path, jpg_file)
#         try:
#             img = Image.open(image_path)
#             debug_print(f"Opening image: {image_path}")
#             img.show()
#             opened += 1
#         except IOError as e:
#             debug_print(f"Unable to open image {image_path}: {str(e)}")

#     debug_print(f"Opened {opened} images")
#     return opened

# # API details for the Hugging Face Stable Diffusion model
# debug_print("Loading HuggingFaceAPIKey from .env...")
# api_key = get_key('.env', 'HuggingFaceAPIKey')
# if not api_key:
#     debug_print("Error: HuggingFaceAPIKey not found in .env")
#     print("Failed: Missing HuggingFaceAPIKey", flush=True)
#     sys.exit(1)
# headers = {"Authorization": f"Bearer {api_key}"}
# API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

# # Async function to send a query to the Hugging Face API
# async def query(payload):
#     debug_print(f"Sending API query: {payload['inputs'][:50]}...")
#     try:
#         response = await asyncio.to_thread(
#             requests.post, API_URL, headers=headers, json=payload, timeout=30  # Increased timeout
#         )
#         debug_print(f"API response status: {response.status_code}")
#         if response.status_code == 402:
#             debug_print("API Error: Payment required (402). Add payment method to Hugging Face account.")
#             print("Failed: Please add a payment method to your Hugging Face account for this model[](https://huggingface.co/settings/billing).", flush=True)
#             return None
#         if response.status_code != 200:
#             debug_print(f"API Error: Status {response.status_code}")
#             return None

#         try:
#             data = response.json()
#             if "error" in data:
#                 debug_print(f"API Error: {data['error']}")
#                 return None
#         except json.JSONDecodeError:
#             return response.content

#     except requests.Timeout:
#         debug_print("API Error: Request timed out after 30 seconds")
#         return None
#     except Exception as e:
#         debug_print(f"API Error: {str(e)}")
#         return None

# # Async function to generate images based on the given prompt
# async def generate_images(prompt: str):
#     debug_print(f"Generating images for prompt: {prompt}")
#     tasks = []
#     for _ in range(4):
#         payload = {
#             "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}"
#         }
#         task = asyncio.create_task(query(payload))
#         tasks.append(task)

#     image_bytes_list = await asyncio.gather(*tasks)
#     saved_images = 0
#     prompt_clean = prompt.replace(" ", "_")

#     for i, image_bytes in enumerate(image_bytes_list):
#         if image_bytes:
#             try:
#                 image_path = f"Data\\{prompt_clean}{i + 1}.jpg"
#                 with open(image_path, "wb") as f:
#                     f.write(image_bytes)
#                 saved_images += 1
#                 debug_print(f"Saved image: {image_path}")
#             except Exception as e:
#                 debug_print(f"Error saving image {i + 1}: {str(e)}")

#     debug_print(f"Saved {saved_images} images")
#     return saved_images

# # Wrapper function
# def GenerateImages(prompt: str):
#     debug_print(f"Processing prompt: {prompt}")
#     prompt = prompt.replace("generate image", "").strip()
#     if not prompt:
#         debug_print("Error: No valid prompt provided")
#         print("Failed: No valid prompt provided", flush=True)
#         return 0

#     try:
#         saved = asyncio.run(generate_images(prompt))
#         opened = open_images(prompt) if saved > 0 else 0
#         if saved > 0 and opened > 0:
#             debug_print(f"Success: Generated and opened {saved} images for '{prompt}'")
#             print(f"Generated {saved} images", flush=True)
#             return saved
#         elif saved == 0:
#             debug_print("Error: No images generated")
#             print("Failed: No images generated", flush=True)
#         else:
#             debug_print(f"Error: Generated {saved} images but failed to open them")
#             print("Failed: Images generated but not opened", flush=True)
#         return 0
#     except Exception as e:
#         debug_print(f"Error generating images for '{prompt}': {str(e)}")
#         print(f"Failed: {str(e)}", flush=True)
#         return 0

# # Main execution
# def main():
#     debug_print("Starting ImageGeneration.py...")
#     data_file = r"Frontend\Files\ImageGeneration.data"
    
#     # Check if file exists
#     if not os.path.exists(data_file):
#         debug_print(f"Error: {data_file} not found")
#         print(f"Failed: ImageGeneration.data not found", flush=True)
#         sys.exit(1)

#     # Check file readability
#     if not os.access(data_file, os.R_OK):
#         debug_print(f"Error: No read permission for {data_file}")
#         print(f"Failed: No read permission for ImageGeneration.data", flush=True)
#         sys.exit(1)

#     try:
#         debug_print(f"Reading {data_file}...")
#         with open(data_file, "r") as f:
#             Data = f.read().strip()
#         debug_print(f"Read data: {Data}")

#         # Handle empty or malformed file
#         if not Data:
#             debug_print("Error: ImageGeneration.data is empty")
#             print("Failed: ImageGeneration.data is empty", flush=True)
#             sys.exit(1)

#         # Parse prompt and status
#         try:
#             Prompt, Status = Data.split(",", 1)
#             Prompt = Prompt.strip()
#             Status = Status.strip()
#             debug_print(f"Parsed prompt: {Prompt}, status: {Status}")
#         except ValueError:
#             debug_print("Error: Malformed ImageGeneration.data, expected 'prompt,True'")
#             print("Failed: Malformed ImageGeneration.data", flush=True)
#             sys.exit(1)

#         if Status == "True":
#             num_images = GenerateImages(Prompt)
#             if num_images > 0:
#                 debug_print(f"Generated {num_images} images")
#                 print(f"Generated {num_images} images", flush=True)
#             else:
#                 debug_print("Failed to generate images")
#                 print("Failed: No images generated", flush=True)

#             debug_print("Resetting ImageGeneration.data to False,False")
#             try:
#                 with open(data_file, "w") as f:
#                     f.write("False,False")
#             except Exception as e:
#                 debug_print(f"Error resetting {data_file}: {str(e)}")
#                 print(f"Failed: Error resetting ImageGeneration.data: {str(e)}", flush=True)
#         else:
#             debug_print("Status is not True, no images generated")
#             print("Failed: Status is not True", flush=True)
#             sys.exit(0)

#     except Exception as e:
#         debug_print(f"Error in main loop: {str(e)}")
#         print(f"Failed: {str(e)}", flush=True)
#         sys.exit(1)

# if __name__ == "__main__":
#     main()





