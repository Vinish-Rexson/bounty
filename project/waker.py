import os
import time
import requests
import threading
import websocket
from datetime import datetime

def wake_app():
    app_url = "https://devop-roz8.onrender.com"  # Replace with your Render URL
    ws_url = f"wss://devop-roz8.onrender.com/ws/chat/1/"  # Replace with a valid chat room ID
    
    while True:
        try:
            # Make HTTP request
            response = requests.get(app_url)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if response.status_code == 200:
                print(f"[{current_time}] HTTP wake-up call successful")
            
            # Try WebSocket connection
            ws = websocket.create_connection(ws_url)
            ws.close()
            print(f"[{current_time}] WebSocket connection successful")
                
        except Exception as e:
            print(f"[{current_time}] Error during wake-up call: {str(e)}")
            
        # Wait for 10 minutes before the next request
        time.sleep(600)  # 600 seconds = 10 minutes

def start_waker():
    waker_thread = threading.Thread(target=wake_app, daemon=True)
    waker_thread.start()