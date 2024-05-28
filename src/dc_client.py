import discord
from discord.ext import commands
from commands import (
    price, 
    ma31, 
    best4Buy, 
    best4Sell, 
    subscribe, 
    unsubscribe
)

# Define the intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)
client = commands.Bot(
    command_prefix = "$$ ",
    intents=intents,
    help_command=help_command
)

client.add_command(price)
client.add_command(ma31)
client.add_command(best4Buy)
client.add_command(best4Sell)
client.add_command(subscribe)
client.add_command(unsubscribe)