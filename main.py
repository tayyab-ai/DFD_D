import os
import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
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

# Global variables (declare at top)
server_running = False

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav', 'ogg', 'm4a'}

# Initialize discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type_from_extension(filename):
    """Determine file type from extension"""
    if not filename:
        return "Unknown"
    
    file_extension = filename.rsplit('.', 1)[1].lower()
    
    if file_extension in ['png', 'jpg', 'jpeg', 'gif']:
        return "Image"
    elif file_extension in ['mp4', 'avi', 'mov']:
        return "Video"
    elif file_extension in ['mp3', 'wav', 'ogg', 'm4a']:
        return "Audio"
    else:
        return "Unknown"

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

        # Secure filename and save
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        app.logger.info(f"Saved file to {file_path}")

        # Simulate processing delay
        time.sleep(1)

        # Generate dummy results based on file type
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

        # Clean up temporary file
        try:
            os.remove(file_path)
            app.logger.info(f"Temporary file removed: {file_path}")
        except Exception as e:
            app.logger.warning(f"Could not remove temporary file: {e}")

        # Return results
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
    """Handle file too large error"""
    return jsonify({
        'error': f'File too large. Maximum size is {MAX_CONTENT_LENGTH // (1024 * 1024)} MB.',
        'success': False
    }), 413

# Discord Bot Events and Commands
@bot.event
async def on_ready():
    """Bot startup event"""
    print(f'🤖 Bot is ready! Logged in as {bot.user}')
    app.logger.info(f"Discord bot started: {bot.user}")

@bot.command()
async def startWebsite(ctx):
    """Start the Flask server"""
    global server_running
    if not server_running:
        app.logger.info("Starting Flask server via bot command")
        port = int(os.environ.get('PORT', 5000))
        threading.Thread(
            target=app.run, 
            args=('0.0.0.0', port), 
            kwargs={'debug': False}
        ).start()
        server_running = True
        await ctx.send(f"✅ Website is now live on port {port}!")
    else:
        await ctx.send("⚠️ Website is already running!")

@bot.command()
async def stopWebsite(ctx):
    """Stop the Flask server (placeholder)"""
    global server_running
    server_running = False
    await ctx.send("🛑 Website stop command received!")

@bot.command()
async def status(ctx):
    """Check server status"""
    global server_running
    if server_running:
        port = int(os.environ.get('PORT', 5000))
        await ctx.send(f"✅ Website is running on port {port}")
    else:
        await ctx.send("❌ Website is not running")

@bot.command()
async def ping(ctx):
    """Simple ping command"""
    await ctx.send(f"🏓 Pong! Latency: {round(bot.latency * 1000)}ms")

@bot.command()
async def help_commands(ctx):
    """Show available commands"""
    embed = discord.Embed(
        title="🤖 Bot Commands",
        description="Available commands for this bot:",
        color=0x00ff00
    )
    embed.add_field(
        name="!startWebsite", 
        value="Start the Flask web server", 
        inline=False
    )
    embed.add_field(
        name="!stopWebsite", 
        value="Stop the Flask web server", 
        inline=False
    )
    embed.add_field(
        name="!status", 
        value="Check website status", 
        inline=False
    )
    embed.add_field(
        name="!ping", 
        value="Check bot latency", 
        inline=False
    )
    await ctx.send(embed=embed)

# Main execution
if __name__ == '__main__':
    try:
        app.logger.info("🚀 Starting Flask server and Discord bot...")
        
        # Get port from environment (Railway sets this automatically)
        port = int(os.environ.get('PORT', 5000))
        
        # Start Flask server in a separate thread
        threading.Thread(
            target=app.run, 
            args=('0.0.0.0', port), 
            kwargs={'debug': False, 'use_reloader': False}
        ).start()
        
        # Update global variable
        server_running = True
        app.logger.info(f"✅ Flask server started on port {port}")
        
        # Get Discord token from environment
        discord_token = os.environ.get('DISCORD_TOKEN')
        if not discord_token:
            app.logger.error("❌ DISCORD_TOKEN environment variable not set!")
            raise EnvironmentError("DISCORD_TOKEN environment variable is required")
        
        # Start Discord bot (this will block)
        app.logger.info("🤖 Starting Discord bot...")
        bot.run(discord_token)
        
    except Exception as e:
        app.logger.error(f"❌ Failed to start application: {e}")
        raise
