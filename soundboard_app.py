import subprocess
import os
import io
import discord
import asyncio
from pathlib import Path
from mutagen import File as MutagenFile
from discord.ext import commands
from mutagen import File
from discord import FFmpegPCMAudio

async def list_soundboard(ctx):
    folder = "soundboard"
    if not os.path.exists(folder):
        await ctx.send("No soundboard folder found.")
        return

    files = [f for f in os.listdir(folder) if f.lower().endswith((".mp3", ".wav", ".ogg"))]
    if not files:
        await ctx.send("No soundboard clips found.")
        return

    embed = discord.Embed(
        title="Soundboard Clips",
        description="List of available soundboard clips:",
        color=discord.Color.green()
    )

    formatted_files = []
    for f in files:
        path = os.path.join(folder, f)
        try:
            audio = File(path)
            duration_sec = int(audio.info.length)
            mins, secs = divmod(duration_sec, 60)
            formatted_files.append(f"- {os.path.splitext(f)[0]} [{mins}:{secs:02d}]")
        except Exception:
            formatted_files.append(f"- {os.path.splitext(f)[0]} [unknown]")

    embed.add_field(name="Clips", value="\n".join(formatted_files), inline=False)
    embed.set_footer(text=f"Total clips: {len(files)}")

    await ctx.send(embed=embed)

async def play_sound_helper(ctx, sound_id, bot):
    # Check user in a voice channel
    if not ctx.author.voice:
        await ctx.send("You must be in a voice channel to play a sound.")
        return

    # Look for file
    filename = None
    candidate = os.path.join("soundboard", f"{sound_id}.wav")
    if os.path.isfile(candidate):
        filename = candidate
    else:
        await ctx.send(f"Sound '{sound_id}' not found.")
        return

    # Send message
    await ctx.send(f"Playing {os.path.basename(filename)}")

    # Now connect to voice channel
    channel = ctx.author.voice.channel
    voice_client = await channel.connect()

    # Play audio
    audio_source = FFmpegPCMAudio(filename)
    voice_client.play(audio_source)
    
    # Wait until finished
    while voice_client.is_playing():
        await asyncio.sleep(1)

    # Disconnect
    voice_client.stop()
    await voice_client.disconnect()

async def convert_to_wav(input_file):
    base, _ = os.path.splitext(input_file)
    output_file = f"{base}.opus"
    subprocess.run([
        "ffmpeg",
        "-y",                # Overwrite if exists
        "-i", input_file,    # Input file path
        "-ar", "16000",      # Sample rate 16kHz
        "-ac", "1",          # Mono (reduces CPU usage)
        "-c:a", "libopus",   # Encode to Opus
        "-b:a", "64k",       # Bitrate (short soundboard clips can use 64 kbps)
        output_file
    ], check=True)
    return output_file

async def sb_upload_helper(ctx):
    if not ctx.message.attachments:
        await ctx.send("Please attach a file.")
        return
    
    attachment = ctx.message.attachments[0]
    filename = os.path.basename(attachment.filename)
    save_path = f"soundboard/{filename}"

    if not filename.lower().endswith((".mp3", ".wav", ".ogg")):
        await ctx.send("Only mp3, wav, or ogg files are supported")
        return
    
    MAX_FILE_SIZE = 2 * 1024 * 1024
    if attachment.size > MAX_FILE_SIZE:
        await ctx.send("File is too large!")
        return
    
    # Reading file into memory
    file_bytes = await attachment.read()

    # Using mutagen to check duration
    audio = MutagenFile(io.BytesIO(file_bytes))
    if not audio or not audio.info:
        await ctx.send("Could not read audio file metadata.")
        return
    
    MAX_DURATION = 30
    duration = audio.info.length
    if duration > MAX_DURATION:
        await ctx.send(f"Audio is too long! Max allowed: {MAX_DURATION}s, your file: {duration:.1f}s")
        return
    
    with open(save_path, "wb") as f:
        f.write(file_bytes)
    await ctx.send(f"File saved as {filename}")

    await convert_to_wav(save_path)