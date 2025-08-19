import os
import discord
from discord.ext import commands
from mutagen import File

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
