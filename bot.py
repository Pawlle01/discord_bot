import discord
from discord.ext import commands

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
    await ctx.send("Hello World! I am Pawle's Goy-Clanker.")

@bot.command()
async def echo(ctx, *, message):
    await ctx.send(f"You said: {message}")

bot.run(token)