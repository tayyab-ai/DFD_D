import os
import logging
import tempfile
import threading
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import time
import discord
from discord.ext import commands
from waitress import serve

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "deepfake-detector-secret-key")

UPLOAD_FOLDER = tempfile.gettempdir()
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav', 'ogg', 'm4a'}

server_running = False
server_lock = threading.Lock()

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type_from_extension(filename):
    if not filename:
        return "Unknown"
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in ['png', 'jpg', 'jpeg', 'gif']:
        return "Image"
    elif ext in ['mp4', 'avi', 'mov']:
        return "Video"
    elif ext in ['mp3', 'wav', 'ogg', 'm4a']:
        return "Audio"
    else:
        return "Unknown"

@app.route('/')
def home():
    app.logger.info("Home page accessed")
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        app.logger.info("File upload request received")
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not supported. Please upload image, video, or audio files.'}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        app.logger.info(f"Saved file to {file_path}")

        # Removed blocking sleep for faster response
        
        file_type = get_file_type_from_extension(filename)
        if file_type == "Image":
            confidence = 0.85
            result_text = f"Testing: {int(confidence * 100)}% Fake"
        elif file_type == "Video":
            confidence = 0.92
            result_text = f"Testing: {int(confidence * 100)}% Fake"
        elif file_type == "Audio":
            confidence = 0.78
            result_text = f"Testing: {int(confidence * 100)}% Fake"
        else:
            confidence = 0.50
            result_text = f"Testing: {int(confidence * 100)}% Unknown"

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
        return jsonify({
            'error': f'File too large. Maximum size is {MAX_CONTENT_LENGTH // (1024 * 1024)} MB.',
            'success': False
        }), 413
    except Exception as e:
        app.logger.error(f"Error processing upload: {e}")
        return jsonify({
            'error': 'An error occurred while processing your file. Please try again.',
            'success': False
        }), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({
        'error': f'File too large. Maximum size is {MAX_CONTENT_LENGTH // (1024 * 1024)} MB.',
        'success': False
    }), 413

@bot.event
async def on_ready():
    print(f'🤖 Bot is ready! Logged in as {bot.user}')
    app.logger.info(f"Discord bot started: {bot.user}")

@bot.command()
async def startWebsite(ctx):
    global server_running
    with server_lock:
        if not server_running:
            port = int(os.environ.get('PORT', 5000))
            threading.Thread(
                target=serve,
                args=(app,),
                kwargs={'host': '0.0.0.0', 'port': port}
            ).start()
            server_running = True
            await ctx.send(f"✅ Website is now live on port {port}!")
        else:
            await ctx.send("⚠️ Website is already running!")

@bot.command()
async def stopWebsite(ctx):
    global server_running
    # Flask server stop is placeholder, not implemented
    server_running = False
    await ctx.send("🛑 Website stop command received! (Not implemented)")

@bot.command()
async def status(ctx):
    if server_running:
        port = int(os.environ.get('PORT', 5000))
        await ctx.send(f"✅ Website is running on port {port}")
    else:
        await ctx.send("❌ Website is not running")

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Latency: {round(bot.latency * 1000)}ms")

@bot.command()
async def help_commands(ctx):
    embed = discord.Embed(
        title="🤖 Bot Commands",
        description="Available commands for this bot:",
        color=0x00ff00
    )
    embed.add_field(name="!startWebsite", value="Start the Flask web server", inline=False)
    embed.add_field(name="!stopWebsite", value="Stop the Flask web server (placeholder)", inline=False)
    embed.add_field(name="!status", value="Check website status", inline=False)
    embed.add_field(name="!ping", value="Check bot latency", inline=False)
    await ctx.send(embed=embed)

if __name__ == '__main__':
    app.logger.info("🚀 Starting Discord bot...")
    discord_token = os.environ.get('DISCORD_TOKEN')
    if not discord_token:
        app.logger.error("❌ DISCORD_TOKEN environment variable not set!")
        raise EnvironmentError("DISCORD_TOKEN environment variable is required")
    bot.run(discord_token)

