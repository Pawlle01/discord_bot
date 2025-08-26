import discord
import aiohttp, asyncio
import datetime as dt
import os
import psutil
import time
from discord.ext import commands

from help_menu import send_help
from soundboard_app import list_soundboard, play_sound_helper, sb_upload_helper

# Vars
download_path = "media_downloads/"

# Intents 
intents = discord.Intents.default()
intents.message_content = True

print("Message Content Intent:", intents.message_content)
print("Presences Intent:", intents.presences)
print("Members Intent:", intents.members)


# Prefix 
bot = commands.Bot(command_prefix="Clanker!", intents=intents, case_insensitive=True)

# Token
token = ""
with open("tokens.txt", 'r') as file:
    token = file.read().split("bot_token=", 1)[1]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def hello(ctx):
    await ctx.send("Hello World! I am Pawle's Clanker.")

@bot.command()
async def download_image(ctx, *, url):
    caller_name = str(ctx.author)
    if caller_name == "pawle":

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:

                if response.status == 200:
                    data = await response.read()
                    filename =  caller_name + dt.datetime.now().strftime(r"%Y-%m-%d_%H%M%S") + "_" + url.split("/")[-1]

                    with open(download_path+filename, "wb") as f:
                        f.write(data)

                    await ctx.send(f"Image downloaded successfully")

                else:
                    await ctx.send(f"Image download failed. Please try again.\nStatus Code: {response.status}")
    else:
        await ctx.send(f"Sorry, you are not permitted to use this command right now. Good try.")

@bot.command()
async def soundboard_upload(ctx):
    await sb_upload_helper(ctx)
    

@bot.command()
async def soundboard_play(ctx, sound_id):
    await play_sound_helper(ctx, sound_id, bot)
    

@bot.command()
async def info(ctx):
    await send_help(ctx) 

@bot.command(name="soundboard_list", help="Shows all available soundboard clips")
async def soundboard_list(ctx):
    await list_soundboard(ctx)
        

bot.run(token)