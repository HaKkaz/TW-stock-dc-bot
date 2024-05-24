import discord
import asyncio
from dotenv import load_dotenv
import os
from discord.ext import commands
import twstock

# Load .env file
load_dotenv()

# Get the specific environment variable
DC_Token = os.getenv('DC_Token')
DC_Channel_Id = 1155856598607085668

# Define the intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
client = commands.Bot(command_prefix = "!", intents=intents)

# events
@client.event
async def on_ready():
    print('start bot successfully')
    channel = client.get_channel(DC_Channel_Id)
    # print(DC_Channel_Id)
    if channel:
        await channel.send('start bot successfully')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == 'hi':
        print('Hello')
        await message.channel.send('Hello')
    await client.process_commands(message)

@client.command()
async def price(ctx, args):
    stock = twstock.realtime.get(args)
    print(stock)
    await ctx.send(stock['info']['name'] + ' 目前價格: ' + stock['realtime']['latest_trade_price'])


client.run(DC_Token)