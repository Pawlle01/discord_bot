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
    # Make sure user is in a voice channel
    if not ctx.author.voice:
        await ctx.send("You are not in a voice channel.")
        return

    channel = ctx.author.voice.channel
    voice_client = await channel.connect()

    # Look for supported file extensions
    supported_exts = [".mp3", ".wav", ".ogg"]
    filename = None
    for ext in supported_exts:
        candidate = os.path.join("soundboard", f"{sound_id}{ext}")
        if os.path.isfile(candidate):
            filename = candidate
            break

    if not filename:
        await ctx.send(f"Sound '{sound_id}' not found.")
        await voice_client.disconnect()
        return

    # Set up FFmpegPCMAudio with streaming
    audio_source = FFmpegPCMAudio(
        executable="/usr/bin/ffmpeg",  # Correct Linux path
        source=filename,
        pipe=True
    )

    # Play audio
    voice_client.play(audio_source)
    await ctx.send(f"Playing {os.path.basename(filename)}")

    # Wait until playback finishes
    while voice_client.is_playing():
        await asyncio.sleep(0.5)

    # Disconnect after done
    await voice_client.disconnect()


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