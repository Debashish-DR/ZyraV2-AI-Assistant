
import os
import subprocess
import requests

def get_device_type(): 
    try:
        if 'ANDROID_ROOT' in os.environ or 'TERMUX_VERSION' in os.environ:
            return "mobile"
        if 'Pythonista' in os.environ:
            return "mobile"
            
        try:
            user_agent = os.environ.get('HTTP_USER_AGENT', '').lower()
            mobile_keywords = ['android', 'iphone', 'ipad', 'mobile']
            if any(keyword in user_agent for keyword in mobile_keywords):
                return "mobile"
        except:
            pass
            
    except Exception as e:
        print(f"[DEVICE_MANAGER] Detection error: {e}")
    
    return "pc"

def is_phone_connected():
    try:
        result = subprocess.run(['adb', 'devices'], 
                              capture_output=True, text=True, timeout=5)
        if 'device' in result.stdout:
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    
    return False

def get_connection_method():
    device_type = get_device_type()
    
    if device_type == "mobile":
        return "direct"
    
    elif device_type == "pc" and is_phone_connected():
        return "adb"
    
    return "none"










#================================================================================
# Device Manager for Mobile/PC Detection and Connection Method


# # Backend/device_manager.py
# import os
# import subprocess
# import requests

# def get_device_type():
#     """
#     Detect if the application is running on a PC or Mobile device.
#     Returns: 'pc' or 'mobile'
#     """
#     try:
#         # Check for Android environment variables (Termux)
#         if 'ANDROID_ROOT' in os.environ or 'TERMUX_VERSION' in os.environ:
#             return "mobile"
        
#         # Check for iOS (Pythonista)
#         if 'Pythonista' in os.environ:
#             return "mobile"
            
#         # Check if running on mobile browser (for web deployment)
#         try:
#             # Simple mobile device check using user agent (for web apps)
#             user_agent = os.environ.get('HTTP_USER_AGENT', '').lower()
#             mobile_keywords = ['android', 'iphone', 'ipad', 'mobile']
#             if any(keyword in user_agent for keyword in mobile_keywords):
#                 return "mobile"
#         except:
#             pass
            
#     except Exception as e:
#         print(f"[DEVICE_MANAGER] Detection error: {e}")
    
#     # Default to PC
#     return "pc"

# def is_phone_connected():
#     """
#     Check if a mobile phone is connected via ADB (for PC-to-phone control)
#     Returns: True if phone is connected and reachable, False otherwise
#     """
#     try:
#         # Try to check if ADB devices are available
#         result = subprocess.run(['adb', 'devices'], 
#                               capture_output=True, text=True, timeout=5)
#         if 'device' in result.stdout:
#             return True
#     except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
#         pass
    
#     return False

# def get_connection_method():
#     """
#     Determine the best connection method for mobile commands
#     Returns: 'direct' (on mobile) or 'adb' (phone connected to PC) or 'none'
#     """
#     device_type = get_device_type()
    
#     if device_type == "mobile":
#         return "direct"  # Running directly on mobile
    
#     elif device_type == "pc" and is_phone_connected():
#         return "adb"     # Phone connected to PC via ADB
    
#     return "none"        # No mobile connection available

# # Example usage
# if __name__ == "__main__":
#     device = get_device_type()
#     connection = get_connection_method()
#     print("=== DEVICE DETECTION ===")
#     print(f"Device Type: {device}")
#     print(f"Connection Method: {connection}")
#     print("=============================")