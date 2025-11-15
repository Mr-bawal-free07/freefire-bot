import requests
import json
from flask import Flask, render_template, request, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'asuwishmynigga' 

BOT_API_URL = "http://127.0.0.1:8080/command"

@app.route('/')
def index():
    """Renders the main control panel page."""
    return render_template('index.html')

@app.route('/action', methods=['POST'])
def handle_action():
    """Handles all form submissions from the new UI."""
    try:
        action = request.form.get('action')
        payload_str = request.form.get('payload')
        
        if not action or payload_str is None:
            flash('Invalid request from client.', 'danger')
            return redirect(url_for('index'))

        bot_payload = {'action': action}
        
        data = json.loads(payload_str)

        if action == 'emote':
            bot_payload.update(data)
            if not bot_payload.get('emote_id') or not bot_payload.get('player_ids'):
                raise ValueError("Emote ID and Player IDs are required.")
            flash(f"Sending emote {bot_payload['emote_id']} to {len(bot_payload['player_ids'])} player(s)...", 'success')

        elif action == 'emote_batch':
            if not isinstance(data, list):
                raise ValueError("A list of assignments is required for emote_batch.")
            bot_payload['assignments'] = data
            flash(f"Sending batch of {len(bot_payload['assignments'])} assigned emotes...", 'success')
            
        elif action == 'join_squad':
            bot_payload.update(data)
            if not bot_payload.get('team_code'):
                 raise ValueError("Team Code is required.")
            flash(f"Attempting to join squad {bot_payload.get('team_code')}...", 'success')

        elif action == 'quick_invite':
            bot_payload.update(data)
            if not bot_payload.get('player_id'):
                 raise ValueError("Your Main Account UID is required.")
            flash('Creating squad and sending invite...', 'success')

        elif action == 'leave_squad':
            bot_payload.update(data)
            flash('Telling bot to leave squad...', 'info')
        
        else:
            flash(f'Unknown action: {action}', 'danger')
            return redirect(url_for('index'))

        response = requests.post(BOT_API_URL, json=bot_payload, timeout=10)
        
        if response.status_code == 200:
            flash(response.json().get('message', 'Command sent successfully!'), 'success')
        else:
            flash(f"Error from bot: {response.status_code} - {response.json().get('error', 'Unknown error')}", 'danger')

    except requests.exceptions.ConnectionError:
        flash('Could not connect to the bot API. Is main.py running?', 'danger')
    except (ValueError, json.JSONDecodeError) as e:
        flash(f'Invalid data provided: {e}', 'danger')
    except Exception as e:
        flash(f'An unexpected error occurred: {e}', 'danger')

    return redirect(url_for('index'))

if __name__ == '__main__':
    print("CLOUD ENGINE Bot Web Panel")
    print("Open your web browser and go to http://127.0.0.1:5000")
    print("Make sure main.py is running first!")
    app.run(host='127.0.0.1', port=5000)