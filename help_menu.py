import discord
from discord.ext import commands

async def send_help(ctx):
    embed = discord.Embed(
        title="Clanker Bot Commands",
        description="Here are the available commands you can use:",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="hello",
        value="Greets the user.\nUsage: `Clanker!hello`",
        inline=False
    )
    
    embed.add_field(
        name="download_image",
        value="Download an image from a URL. Restricted to user 'pawle'.\nUsage: `Clanker!download_image <url>`",
        inline=False
    )

    embed.add_field(
        name="soundboard_upload",
        value="Upload a sound file to the bot's soundboard.\nSupported: mp3, wav, ogg.\nUsage: `Clanker!soundboard_upload` (attach file)",
        inline=False
    )

    embed.add_field(
        name="soundboard_play",
        value="Play a sound from the soundboard.\nUsage: `Clanker!soundboard_play <sound_id>`",
        inline=False
    )

    embed.set_footer(text="Clanker Bot • Developed by Pawle")
    await ctx.send(embed=embed)
