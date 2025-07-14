import os
import glob
from pathlib import Path
from pyrogram import Client, filters
from vars import ADMINS

def clean_downloads():
    """Clean everything in downloads directory"""
    try:
        # Create downloads directory if it doesn't exist
        os.makedirs("downloads", exist_ok=True)
        
        # Remove all files in downloads directory
        for file in glob.glob("downloads/*"):
            try:
                if os.path.isfile(file):
                    os.remove(file)
                    print(f"Removed from downloads: {file}")
            except Exception as e:
                print(f"Error removing {file}: {e}")
    except Exception as e:
        print(f"Error cleaning downloads: {e}")

def clean_media_files():
    """Clean images and videos except wm.png"""
    try:
        # Define media formats to clean
        image_formats = ["*.jpg", "*.jpeg", "*.png"]
        video_formats = ["*.mp4", "*.mkv", "*.webm"]
        temp_formats = ["*.part", "*.ytdl"]
        
        # Combine all formats
        formats_to_clean = image_formats + video_formats + temp_formats
        
        # Clean files in root directory
        for format_pattern in formats_to_clean:
            for file in glob.glob(format_pattern):
                try:
                    # Skip wm.png
                    if file == "wm.png":
                        continue
                        
                    if os.path.isfile(file):
                        os.remove(file)
                        print(f"Removed from root: {file}")
                except Exception as e:
                    print(f"Error removing {file}: {e}")
    except Exception as e:
        print(f"Error cleaning media files: {e}")

def clean_all():
    """Clean all specified files"""
    clean_downloads()
    clean_media_files()

# Command handler for /clean
async def handle_clean_command(client: Client, message):
    """Handle the /clean command"""
    try:
        # Only allow admins to use this command
        if message.from_user.id not in ADMINS:
            await message.reply_text("⚠️ You are not authorized to use this command.")
            return
            
        # Send initial message
        status_msg = await message.reply_text("🧹 Cleaning files...")
        
        # Clean all files
        clean_all()
        
        # Update status message
        await status_msg.edit_text("✅ Cleanup completed!\n- Cleaned downloads directory\n- Removed media files (except wm.png)\n- Removed .part and .ytdl files")
        
    except Exception as e:
        await message.reply_text(f"❌ Error during cleanup: {str(e)}")

# Register command handler
def register_clean_handler(bot: Client):
    """Register the clean command handler"""
    bot.add_handler(filters.command("clean") & filters.private, handle_clean_command)

# Clean on startup
clean_all()