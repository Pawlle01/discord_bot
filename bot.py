import discord
import aiohttp, asyncio
import datetime as dt
import os
from discord.ext import commands

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
                    await ctx.send(f"Image download failed. Please try again.\nStatus Code: {response.status_code}")
    else:
        await ctx.send(f"Sorry, you are not permitted to use this command right now. Good try.")


@bot.command()
async def soundboard(ctx, sound_id):
    if not ctx.author.voice:
        await ctx.send("You are not currently in a voice channel.")
        return
    
    channel = ctx.author.voice.channel
    voice_client = await channel.connect()

    supported_exts = [".mp3", ".wav", ".ogg"]
    filename = None
    for ext in supported_exts:
        candidate = os.path.join("soundboard", f"{sound_id}{ext}")
        if os.path.isfile(candidate):
            filename = candidate
            break

    if not filename:
        await ctx.send(f"Sound {sound_id} not found (tried {supported_exts})")
        await voice_client.disconnect()
        return

    #filename = "soundboard/" + str(sound_id) + ".mp3"
    audio_source = discord.FFmpegPCMAudio(executable=r"C:\Users\pgall\Downloads\ffmpeg-2025-08-14-git-cdbb5f1b93-essentials_build\bin\ffmpeg.exe", source=filename)
    
    def after_playing(error):
        if error:
            print(f"Error during playback: {error}")
        coro = voice_client.disconnect()
        fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
        try:
            fut.result()
        except:
            pass

    voice_client.play(audio_source, after=after_playing)
    await ctx.send(f"Playing {os.path.basename(filename)}")
    
    


        

bot.run(token)