import os
import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import tempfile
import time
import magic  # python-magic for MIME type detection
import discord
from discord.ext import commands
import threading

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "deepfake-detector-secret-key")

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Allowed file extensions (for basic check)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav', 'ogg', 'm4a'}

# Initialize discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)
server_running = False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    app.logger.info("Home page accessed")
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        app.logger.info("File upload request received")
        if 'file' not in request.files:
            app.logger.warning("No file part in request")
            return jsonify({'error': 'No file selected'}), 400

        file = request.files['file']

        if file.filename == '':
            app.logger.warning("No file selected")
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            app.logger.warning(f"File type not allowed (extension): {file.filename}")
            return jsonify({'error': 'File type not supported. Please upload image, video, or audio files.'}), 400

        # Verify MIME type using file content
        file_content = file.read(2048)
        file.seek(0)  # reset pointer

        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(file_content)

        allowed_mime_types = [
            'image/png', 'image/jpeg', 'image/gif', 
            'video/mp4', 'video/x-msvideo', 'video/quicktime',
            'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp4', 'audio/x-m4a'
        ]

        if mime_type not in allowed_mime_types:
            app.logger.warning(f"File MIME type not allowed: {mime_type}")
            return jsonify({'error': 'File MIME type not supported.'}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        app.logger.info(f"Saved file to {file_path}")

        time.sleep(1)  # simulate processing delay

        file_extension = filename.rsplit('.', 1)[1].lower()
        if file_extension in ['png', 'jpg', 'jpeg', 'gif']:
            file_type = "Image"
            confidence = 0.85
            result_text = f"Testing: {int(confidence * 100)}% Fake"
        elif file_extension in ['mp4', 'avi', 'mov']:
            file_type = "Video"
            confidence = 0.92
            result_text = f"Testing: {int(confidence * 100)}% Fake"
        else:
            file_type = "Audio"
            confidence = 0.78
            result_text = f"Testing: {int(confidence * 100)}% Fake"

        try:
            os.remove(file_path)
            app.logger.info(f"Temporary file removed: {file_path}")
        except Exception as e:
            app.logger.warning(f"Could not remove temporary file: {e}")

        response = {
            'success': True,
            'result': result_text,
            'confidence': confidence,
            'file_type': file_type,
            'filename': filename,
            'message': 'Analysis complete! This is a prototype with dummy results.'
        }

        app.logger.info(f"Analysis complete for {filename}")
        return jsonify(response)

    except RequestEntityTooLarge:
        app.logger.warning("File too large uploaded")
        return jsonify({'error': f'File too large. Maximum size is {MAX_CONTENT_LENGTH // (1024 * 1024)} MB.', 'success': False}), 413
    except Exception as e:
        app.logger.error(f"Error processing upload: {e}")
        return jsonify({'error': 'An error occurred while processing your file. Please try again.', 'success': False}), 500

# Discord bot events and commands stay the same (not shown here for brevity)

# Run flask and bot
if __name__ == '__main__':
    try:
        app.logger.info("Starting Flask server and Discord bot")
        threading.Thread(target=app.run, args=('0.0.0.0', 5000), kwargs={'debug': False}).start()
        global server_running
        server_running = True
        token = os.getenv('DISCORD_TOKEN')
        if token is None:
            raise EnvironmentError("DISCORD_TOKEN environment variable is not set.")
        bot.run(token)
    except Exception as e:
        app.logger.error(f"Bot or server failed to start: {e}")
