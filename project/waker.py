import os
import time
import requests
import threading
from datetime import datetime

def wake_app():
    app_url = "https://devop-roz8.onrender.com"  # Replace with your Render URL
    
    while True:
        try:
            # Make a GET request to your app
            response = requests.get(app_url)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if response.status_code == 200:
                print(f"[{current_time}] Wake-up call successful")
            else:
                print(f"[{current_time}] Wake-up call failed with status code: {response.status_code}")
                
        except Exception as e:
            print(f"[{current_time}] Error during wake-up call: {str(e)}")
            
        # Wait for 10 minutes before the next request
        time.sleep(600)  # 600 seconds = 10 minutes

def start_waker():
    waker_thread = threading.Thread(target=wake_app, daemon=True)
    waker_thread.start()