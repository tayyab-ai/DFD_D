import os
import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import tempfile
import time
import discord
from discord.ext import commands
import threading

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "deepfake-detector-secret-key")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

server_running = False

UPLOAD_FOLDER = tempfile.gettempdir()
MAX_CONTENT_LENGTH = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav', 'ogg', 'm4a'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

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
        return jsonify({'error': 'An error occurred while processing your file. Please try again.', 'success': False}), 500

@app.errorhandler(413)
def too_large(e):
    app.logger.warning("File too large uploaded")
    return jsonify({'error': f'File too large. Maximum size is {MAX_CONTENT_LENGTH // (1024 * 1024)} MB.', 'success': False}), 413

@bot.event
async def on_ready():
    print(f'Bot ready as {bot.user}')
    app.logger.info(f"Bot started: {bot.user}")

@bot.command()
async def startWebsite(ctx):
    global server_running
    public_url = os.getenv('PUBLIC_URL', 'http://localhost:5000')
    if not server_running:
        app.logger.info("Starting Flask server via bot command")
        threading.Thread(target=app.run, args=('0.0.0.0', 5000), kwargs={'debug': False}).start()
        server_running = True
        await ctx.send(f"Website live: {public_url}")
    else:
        await ctx.send("Website already running!")

@bot.command()
async def status(ctx):
    public_url = os.getenv('PUBLIC_URL', 'http://localhost:5000')
    if server_running:
        await ctx.send(f"Website running at {public_url}")
    else:
        await ctx.send("Website not running.")

token = os.getenv('DISCORD_TOKEN')
if token is None:
    raise EnvironmentError("DISCORD_TOKEN environment variable is not set.")

if __name__ == '__main__':
    try:
        app.logger.info("Starting Flask server and Discord bot")
        threading.Thread(target=app.run, args=('0.0.0.0', 5000), kwargs={'debug': False}).start()
        server_running = True
        bot.run(token)
    except Exception as e:
        app.logger.error(f"Bot or server failed to start: {e}")
