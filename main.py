import os
import logging
import tempfile
import threading
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import discord
from discord.ext import commands
from waitress import serve

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
public_url = os.environ.get('PUBLIC_URL', 'http://localhost')

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
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not supported.'}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        app.logger.info(f"Saved file to {file_path}")

        file_type = get_file_type_from_extension(filename)
        confidence = 0.5
        if file_type == "Image":
            confidence = 0.85
        elif file_type == "Video":
            confidence = 0.92
        elif file_type == "Audio":
            confidence = 0.78
        result_text = f"Testing: {int(confidence * 100)}% Fake"

        try:
            os.remove(file_path)
        except:
            pass

        return jsonify({
            'success': True,
            'result': result_text,
            'confidence': confidence,
            'file_type': file_type,
            'filename': filename,
            'message': 'Analysis complete! This is a prototype with dummy results.'
        })

    except RequestEntityTooLarge:
        return jsonify({
            'error': f'File too large. Max size {MAX_CONTENT_LENGTH // (1024 * 1024)} MB.',
            'success': False
        }), 413
    except Exception as e:
        app.logger.error(f"Upload error: {e}")
        return jsonify({'error': 'An error occurred, try again.', 'success': False}), 500

@bot.event
async def on_ready():
    print(f'🤖 Bot ready as {bot.user}')
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
            await ctx.send(f"✅ Website is live: {public_url}")
        else:
            await ctx.send("⚠️ Website already running!")

@bot.command()
async def stopWebsite(ctx):
    global server_running
    # Stopping Flask server is complex in threads, so just notify
    server_running = False
    await ctx.send("🛑 Received stop command. (Server shutdown not implemented)")

@bot.command()
async def status(ctx):
    if server_running:
        await ctx.send(f"✅ Website running at {public_url}")
    else:
        await ctx.send("❌ Website is not running")

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Latency: {round(bot.latency * 1000)}ms")

@bot.command()
async def help_commands(ctx):
    embed = discord.Embed(title="🤖 Bot Commands", description="Commands:", color=0x00ff00)
    embed.add_field(name="!startWebsite", value="Start the website")
    embed.add_field(name="!stopWebsite", value="Stop the website (placeholder)")
    embed.add_field(name="!status", value="Check website status")
    embed.add_field(name="!ping", value="Bot latency")
    await ctx.send(embed=embed)

if __name__ == '__main__':
    try:
        token = os.environ.get('DISCORD_TOKEN')
        if not token:
            raise EnvironmentError("DISCORD_TOKEN not set.")
        print("🚀 Starting Discord bot...")
        bot.run(token)
    except Exception as e:
        logging.error(f"Startup failed: {e}")
