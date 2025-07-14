import os
import re
import time
import mmap
import math
import aiohttp
import aiofiles
import asyncio
import logging
import datetime
import requests
import subprocess
import concurrent.futures
from io import BytesIO
from pathlib import Path
from base64 import b64decode
from urllib.parse import urljoin
from pyrogram import Client, filters
from pyrogram.types import Message
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import m3u8

from utils import progress_bar
from vars import *

TOOLS_DIR = os.path.join(os.path.dirname(__file__), "tools")
MP4DECRYPT = os.path.join(TOOLS_DIR, "mp4decrypt")

def duration(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return float(result.stdout)

def get_mps_and_keys(api_url):
    response = requests.get(api_url)
    response_json = response.json()
    return response_json.get('mpd_url'), response_json.get('keys')

def exec(cmd):
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.stdout.decode()

def pull_run(work, cmds):
    with concurrent.futures.ThreadPoolExecutor(max_workers=work) as executor:
        list(executor.map(exec, cmds))

async def aio(url, name):
    k = f'{name}.pdf'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                async with aiofiles.open(k, mode='wb') as f:
                    await f.write(await resp.read())
    return k

async def pdf_download(url, file_name, chunk_size=1024 * 10):
    if os.path.exists(file_name):
        os.remove(file_name)
    r = requests.get(url, stream=True)
    with open(file_name, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                fd.write(chunk)
    return file_name

def parse_vid_info(info):
    lines = info.strip().split("\n")
    results = []
    seen = set()
    for line in lines:
        if "[" in line or "---" in line:
            continue
        while "  " in line:
            line = line.replace("  ", " ")
        parts = line.split("|")[0].split(" ", 2)
        if len(parts) >= 3 and "RESOLUTION" not in parts[2] and "audio" not in parts[2]:
            if parts[2] not in seen:
                seen.add(parts[2])
                results.append((parts[0], parts[2]))
    return results

def vid_info(info):
    lines = info.strip().split("\n")
    result = {}
    seen = set()
    for line in lines:
        if "[" in line or "---" in line:
            continue
        while "  " in line:
            line = line.replace("  ", " ")
        parts = line.split("|")[0].split(" ", 3)
        if len(parts) >= 3 and "RESOLUTION" not in parts[2] and "audio" not in parts[2]:
            if parts[2] not in seen:
                seen.add(parts[2])
                result[parts[2]] = parts[0]
    return result

def old_download(url, file_name, chunk_size=1024 * 10):
    if os.path.exists(file_name):
        os.remove(file_name)
    r = requests.get(url, stream=True)
    with open(file_name, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                fd.write(chunk)
    return file_name

def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

def time_name():
    return datetime.datetime.now().strftime("%Y-%m-%d %H%M%S") + ".mp4"

def decrypt_file(file_path, key):
    if not os.path.exists(file_path):
        return False
    key = key.encode()
    with open(file_path, "r+b") as f:
        size = os.path.getsize(file_path)
        if size == 0:
            return False
        with mmap.mmap(f.fileno(), length=min(28, size), access=mmap.ACCESS_WRITE) as mm:
            for i in range(len(mm)):
                mm[i] ^= key[i] if i < len(key) else i
    return True

async def run(cmd):
    proc = await asyncio.create_subprocess_shell(cmd,
                                                 stdout=asyncio.subprocess.PIPE,
                                                 stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    if stdout:
        return f"[stdout]\n{stdout.decode()}"
    if stderr:
        return f"[stderr]\n{stderr.decode()}"
    return f"[exit code: {proc.returncode}]"

# Decryption, splitting, upload, etc. functions continue as previously fixed
# ...

