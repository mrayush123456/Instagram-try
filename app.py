from flask import Flask, request, render_template, redirect, url_for
from instagrapi import Client
import time

app = Flask(__name__)

# Instagram Login Function
def instagram_login(username, password):
    try:
        cl = Client()
        cl.login(username, password)
        return cl
    except Exception as e:
        return None, f"Login failed: {e}"

# Send Messages Function
def send_messages(cl, choice, target, messages, delay):
    try:
        if choice == "inbox":
            user_id = cl.user_id_from_username(target)
            for message in messages:
                cl.direct_send(message, [user_id])
                time.sleep(delay)
        elif choice == "group":
            for message in messages:
                cl.direct_send(message, thread_id=target)
                time.sleep(delay)
        return "Messages sent successfully!"
    except Exception as e:
        return f"Failed to send messages: {e}"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        choice = request.form.get("choice")
        target = request.form.get("target")
        delay = int(request.form.get("delay"))
        message_file = request.files.get("message_file")

        try:
            messages = message_file.read().decode("utf-8").splitlines()
        except Exception as e:
            return f"Error reading message file: {e}"

        cl, login_msg = instagram_login(username, password)
        if not cl:
            return f"<h3>{login_msg}</h3>"

        send_status = send_messages(cl, choice, target, messages, delay)
        return f"<h3>{send_status}</h3>"

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
  
