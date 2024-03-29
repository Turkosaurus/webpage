# bot.py
import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(f'{client.user} is connected to {guild.name} (id: {guild.id})')

    print(guild.members[0])

    members = '\n - '.join([member.name for member in guild.members])
    print(members)
    print(f'Guild Members:\n - {members}')

client.run(TOKEN)