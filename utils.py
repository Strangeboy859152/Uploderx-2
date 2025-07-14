import random  
import time  
import math  
import os  
from vars import CREDIT  
from pyrogram.errors import FloodWait  
from datetime import datetime,timedelta  

class Timer:  
    def __init__(self, time_between=5):  
        self.start_time = time.time()  
        self.time_between = time_between  

    def can_send(self):  
        if time.time() > (self.start_time + self.time_between):  
            self.start_time = time.time()  
            return True  
        return False  

#lets do calculations  
def hrb(value, digits= 2, delim= "", postfix=""):  
    """Return a human-readable file size.  
    """  
    if value is None:  
        return None  
    chosen_unit = "B"  
    for unit in ("KB", "MB", "GB", "TB"):  
        if value > 1000:  
            value /= 1024  
            chosen_unit = unit  
        else:  
            break  
    return f"{value:.{digits}f}" + delim + chosen_unit + postfix  

def hrt(seconds, precision = 0):  
    """Return a human-readable time delta as a string.  
    """  
    pieces = []  
    value = timedelta(seconds=seconds)  

    if value.days:  
        pieces.append(f"{value.days}day")  

    seconds = value.seconds  

    if seconds >= 3600:  
        hours = int(seconds / 3600)  
        pieces.append(f"{hours}hr")  
        seconds -= hours * 3600  

    if seconds >= 60:  
        minutes = int(seconds / 60)  
        pieces.append(f"{minutes}min")  
        seconds -= minutes * 60  

    if seconds > 0 or not pieces:  
        pieces.append(f"{seconds}sec")  

    if not precision:  
        return "".join(pieces)  

    return "".join(pieces[:precision])  

timer = Timer()  

async def progress_bar(current, total, reply, start):
    if timer.can_send():
        now = time.time()
        diff = now - start
        if diff < 1:
            return

        perc = f"{current * 100 / total:.1f}%"
        elapsed_time = round(diff)
        speed = current / elapsed_time if elapsed_time > 0 else 0
        boosted_speed = speed + (8 * 1024 * 1024)  # 8 MB/s boost
        remaining_bytes = total - current
        eta = hrt(remaining_bytes / speed, precision=1) if speed > 0 else "-"
        sp = str(hrb(boosted_speed)) + "/s"
        tot = hrb(total)
        cur = hrb(current)

        bar_length = 14
        completed_length = int(current * bar_length / total)
        remaining_length = bar_length - completed_length

        completed_symbol = "🟩"
        remaining_symbol = "⬜"
        progress_bar = completed_symbol * completed_length + remaining_symbol * remaining_length

        try:
            await reply.edit(
                f"🔄 𝚄𝙿𝙻𝙾𝙰𝙳 𝚂𝚃𝙰𝚃𝚄𝚂\n\n"
                f"`{progress_bar}`\n\n"
                f"🧮 ᴘʀᴏɢʀᴇꜱꜱ : {perc}\n"
                f"🚀 ꜱᴘᴇᴇᴅ : {sp}\n"
                f"📦 ᴅᴏɴᴇ : {cur} / {tot}\n"
                f"⏳ ᴇᴛᴀ : {eta}\n\n"
                f"✨ ᴘᴏᴡᴇʀᴇᴅ ʙʏ {CREDIT.upper()}"
            )
        except FloodWait as e:
            time.sleep(e.x)