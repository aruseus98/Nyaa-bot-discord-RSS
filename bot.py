import discord
from config.config import DISCORD_TOKEN
from events.events import MyBot

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

client = MyBot(intents=intents)
client.run(DISCORD_TOKEN)
