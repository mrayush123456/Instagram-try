from flask import Flask, request, render_template_string
from instagrapi import Client
import time

app = Flask(__name__)

# HTML template for the web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Message Sender</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            color: #333;
        }
        .container {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            width: 400px;
        }
        h1 {
            text-align: center;
            color: #555;
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input, select, button {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 14px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            background-color: #45a049;
        }
        .info {
            font-size: 12px;
            color: #666;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Instagram Automation</h1>
        <form action="/" method="POST" enctype="multipart/form-data">
            <label for="username">Instagram Username:</label>
            <input type="text" id="username" name="username" placeholder="Enter your username" required>

            <label for="password">Instagram Password:</label>
            <input type="password" id="password" name="password" placeholder="Enter your password" required>

            <label for="choice">Target Type:</label>
            <select id="choice" name="choice" required>
                <option value="inbox">Inbox</option>
                <option value="group">Group Chat</option>
            </select>

            <label for="target_username">Target Username (for Inbox):</label>
            <input type="text" id="target_username" name="target_username" placeholder="Enter target username">

            <label for="thread_id">Group Thread ID (for Group Chat):</label>
            <input type="text" id="thread_id" name="thread_id" placeholder="Enter group thread ID">

            <label for="message_file">Message File (TXT):</label>
            <input type="file" id="message_file" name="message_file" required>
            <p class="info">Upload a TXT file with messages, one message per line.</p>

            <label for="delay">Delay Between Messages (Seconds):</label>
            <input type="number" id="delay" name="delay" placeholder="Enter delay in seconds" required>

            <button type="submit">Send Messages</button>
        </form>
    </div>
</body>
</html>
'''

# Login function using Instagram private API
def instagram_login(username, password):
    try:
        cl = Client()
        cl.login(username, password)
        print("[SUCCESS] Logged into Instagram!")
        return cl
    except Exception as e:
        print(f"[ERROR] Login failed: {e}")
        return None

# Function to send messages
def send_messages(cl, choice, target_username, thread_id, messages, delay):
    try:
        if choice == "inbox":
            user_id = cl.user_id_from_username(target_username)
            for message in messages:
                cl.direct_send(message, [user_id])
                print(f"[SUCCESS] Sent to {target_username}: {message}")
                time.sleep(delay)
        elif choice == "group":
            for message in messages:
                cl.direct_send(message, thread_id=thread_id)
                print(f"[SUCCESS] Sent to group {thread_id}: {message}")
                time.sleep(delay)
        print("[INFO] All messages sent successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to send messages: {e}")

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Collect form data
        username = request.form.get("username")
        password = request.form.get("password")
        choice = request.form.get("choice")
        target_username = request.form.get("target_username")
        thread_id = request.form.get("thread_id")
        delay = int(request.form.get("delay"))
        message_file = request.files["message_file"]

        # Read messages from uploaded file
        try:
            messages = [line.strip() for line in message_file.read().decode("utf-8").splitlines()]
        except Exception as e:
            return f"<p>Error reading file: {e}</p>"

        # Login to Instagram
        cl = instagram_login(username, password)
        if not cl:
            return "<p>Login failed. Please check your credentials and try again.</p>"

        # Send messages
        send_messages(cl, choice, target_username, thread_id, messages, delay)
        return "<p>Messages sent successfully!</p>"

    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(debug=True)
        
