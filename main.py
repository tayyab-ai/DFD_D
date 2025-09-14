import os
import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import tempfile
import time
import discord
from discord.ext import commands
import threading

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "deepfake-detector-secret-key")

# Create Discord bot with intents
intents = discord.Intents.default()
intents.message_content = True  # Allow bot to read message content
intents.messages = True  # Allow bot to receive messages
bot = commands.Bot(command_prefix='!', intents=intents)

server_running = False

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav', 'ogg', 'm4a'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    """Home page route"""
    app.logger.info("Home page accessed")
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and return dummy deepfake detection results"""
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
            app.logger.warning(f"File type not allowed: {file.filename}")
            return jsonify({'error': 'File type not supported. Please upload image, video, or audio files.'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            app.logger.info(f"Processing file: {filename}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            time.sleep(1)
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
    except Exception as e:
        app.logger.error(f"Error processing upload: {e}")
        return jsonify({
            'error': 'An error occurred while processing your file. Please try again.',
            'success': False
        }), 500


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    app.logger.warning("File too large uploaded")
    return jsonify({
        'error': f'File too large. Maximum size is {MAX_CONTENT_LENGTH // (1024 * 1024)} MB.',
        'success': False
    }), 413


@bot.event
async def on_ready():
    """Bot startup event"""
    print(f'Bot ready as {bot.user}')
    app.logger.info(f"Bot started: {bot.user}")


@bot.command()
async def startWebsite(ctx):
    """Start the Flask server"""
    global server_running
    if not server_running:
        app.logger.info("Starting Flask server via bot command")
        threading.Thread(target=app.run, args=('0.0.0.0', 5000), kwargs={'debug': False}).start()
        server_running = True
        await ctx.send("Website live: https://dfdd-production.up.railway.app")
    else:
        await ctx.send("Website already running!")


@bot.command()
async def status(ctx):
    """Check server status"""
    if server_running:
        await ctx.send("Website running at https://dfdd-production.up.railway.app")
    else:
        await ctx.send("Website not running.")


# Fetch token from environment variable securely
token = os.getenv('DISCORD_TOKEN')
if token is None:
    raise EnvironmentError("DISCORD_TOKEN environment variable is not set.")


# Start Flask server and bot
if __name__ == '__main__':
    try:
        app.logger.info("Starting Flask server and Discord bot")
        threading.Thread(target=app.run, args=('0.0.0.0', 5000), kwargs={'debug': False}).start()
        server_running = True
        bot.run(token)
    except Exception as e:
        app.logger.error(f"Bot or server failed to start: {e}")
