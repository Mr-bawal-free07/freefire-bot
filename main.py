import os
from flask import Flask, render_template, request, flash, redirect
import requests
import json
import threading
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key_123'

# Simple bot status
bot_status = {
    "online": False,
    "last_activity": None,
    "current_action": "Idle"
}

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Free Fire Bot Control Panel</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #1a1a2e, #16213e);
                color: white; 
                padding: 20px;
                margin: 0;
            }
            .container { 
                max-width: 900px; 
                margin: 0 auto; 
            }
            .header {
                text-align: center;
                padding: 20px;
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                margin-bottom: 20px;
            }
            .card { 
                background: rgba(255,255,255,0.1); 
                padding: 25px; 
                margin: 15px 0; 
                border-radius: 15px;
                border: 1px solid rgba(255,255,255,0.2);
            }
            .btn { 
                background: linear-gradient(45deg, #007bff, #0056b3);
                color: white; 
                padding: 12px 24px; 
                border: none; 
                border-radius: 8px; 
                cursor: pointer; 
                margin: 8px;
                font-size: 14px;
                transition: all 0.3s;
            }
            .btn:hover { 
                background: linear-gradient(45deg, #0056b3, #004494);
                transform: translateY(-2px);
            }
            .status-online { color: #00ff00; font-weight: bold; }
            .status-offline { color: #ff4444; font-weight: bold; }
            .input-group { margin: 15px 0; }
            input {
                padding: 10px;
                border: none;
                border-radius: 5px;
                margin: 5px;
                width: 200px;
            }
            .command-log {
                background: rgba(0,0,0,0.3);
                padding: 15px;
                border-radius: 8px;
                max-height: 200px;
                overflow-y: auto;
                margin-top: 15px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎮 Free Fire Bot Control Panel</h1>
                <p>Control your Free Fire bot remotely</p>
            </div>
            
            <div class="card">
                <h2>🤖 Bot Status</h2>
                <p>Status: <span class="status-online">🟢 Online</span></p>
                <p>Last Activity: <span id="lastActivity">Just now</span></p>
                <p>Current Action: <span id="currentAction">Ready</span></p>
            </div>

            <div class="card">
                <h2>⚡ Quick Actions</h2>
                <button class="btn" onclick="sendCommand('emote_all')">🎭 Send Emote to All</button>
                <button class="btn" onclick="sendCommand('join_squad')">👥 Join Squad</button>
                <button class="btn" onclick="sendCommand('leave_squad')">🚪 Leave Squad</button>
                <button class="btn" onclick="sendCommand('quick_invite')">📨 Quick Invite</button>
            </div>

            <div class="card">
                <h2>🎯 Custom Emote</h2>
                <div class="input-group">
                    <input type="text" id="player_id" placeholder="Player UID (e.g., 1234567890)">
                    <input type="text" id="emote_id" placeholder="Emote ID (e.g., 101)">
                    <button class="btn" onclick="sendCustomCommand()">🚀 Send Custom Emote</button>
                </div>
            </div>

            <div class="card">
                <h2>📝 Command Log</h2>
                <div class="command-log" id="commandLog">
                    <div>✅ Panel loaded successfully</div>
                    <div>🟢 Bot is ready to receive commands</div>
                </div>
            </div>
        </div>

        <script>
            let commandCount = 0;

            function addToLog(message) {
                const log = document.getElementById('commandLog');
                const timestamp = new Date().toLocaleTimeString();
                log.innerHTML += `<div>${timestamp} - ${message}</div>`;
                log.scrollTop = log.scrollHeight;
                commandCount++;
            }

            function sendCommand(action) {
                addToLog(`📤 Sending command: ${action}`);
                
                fetch('/command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: action })
                }).then(response => response.json())
                .then(data => {
                    addToLog(`✅ ${data.message}`);
                    updateStatus();
                })
                .catch(error => {
                    addToLog(`❌ Error: ${error}`);
                });
            }

            function sendCustomCommand() {
                const playerId = document.getElementById('player_id').value;
                const emoteId = document.getElementById('emote_id').value;
                
                if (!playerId || !emoteId) {
                    addToLog('❌ Please enter both Player UID and Emote ID');
                    return;
                }
                
                addToLog(`📤 Sending emote ${emoteId} to player ${playerId}`);
                
                fetch('/command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        action: 'custom_emote',
                        player_id: playerId,
                        emote_id: emoteId
                    })
                }).then(response => response.json())
                .then(data => {
                    addToLog(`✅ ${data.message}`);
                    updateStatus();
                })
                .catch(error => {
                    addToLog(`❌ Error: ${error}`);
                });
            }

            function updateStatus() {
                fetch('/status')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('lastActivity').textContent = data.last_activity || 'Never';
                        document.getElementById('currentAction').textContent = data.current_action || 'Ready';
                    });
            }

            // Update status every 3 seconds
            setInterval(updateStatus, 3000);
        </script>
    </body>
    </html>
    """

@app.route('/status')
def status():
    return json.dumps(bot_status)

@app.route('/command', methods=['POST'])
def handle_command():
    try:
        data = request.get_json()
        action = data.get('action')
        
        # Update bot status
        bot_status["last_activity"] = time.strftime("%Y-%m-%d %H:%M:%S")
        bot_status["current_action"] = action
        bot_status["online"] = True
        
        response_message = f"Command '{action}' received successfully!"
        
        # Handle different actions
        if action == 'custom_emote':
            player_id = data.get('player_id')
            emote_id = data.get('emote_id')
            response_message = f"Sent emote {emote_id} to player {player_id}"
        elif action == 'emote_all':
            response_message = "Sending emote to all players in lobby"
        elif action == 'join_squad':
            response_message = "Joining squad..."
        elif action == 'leave_squad':
            response_message = "Leaving current squad"
        elif action == 'quick_invite':
            response_message = "Sending quick invites..."
        
        response = {"status": "success", "message": response_message}
        
        # Simulate bot processing
        def process_command():
            time.sleep(3)
            bot_status["current_action"] = "Ready"
        
        threading.Thread(target=process_command).start()
        
        return json.dumps(response)
    
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Free Fire Bot Web Panel Starting on port {port}...")
    print("📧 Control Panel will be available at the provided URL")
    print("⚡ Bot is ready to receive commands!")
    app.run(host='0.0.0.0', port=port, debug=False)
