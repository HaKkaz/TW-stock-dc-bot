import discord
import os
import twstock
from dotenv import load_dotenv
from discord.ext import commands
from twstock import analytics
import message

# Load .env file
load_dotenv(override=True)

# Get the specific environment variable
DC_Token = os.getenv('DC_Token')
DC_Channel_Id = int(os.getenv('DC_Channel_Id'))

# Define the intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)
client = commands.Bot(
    command_prefix = "!",
    intents=intents,
    help_command=help_command
)

# events
@client.event
async def on_ready():
    print('start bot successfully')

@client.command()
async def price(ctx, stock_code: str):
    """ 
     [stock_code]: 取得指定股票的即時價格
    """
    stock = twstock.realtime.get(stock_code)
    if stock['success']:
        await ctx.send(message.price_message(stock))
    else:
        await ctx.send('error: ' + stock['rtmessage'])

@client.command()
async def ma31(ctx, stock_code: str, days: str):
    """ 
    [stock_code] [days]: 取得指定股票的 31 日內指定天數的移動平均線
    """
    try:
        int(days)
    except ValueError:
        await ctx.send('days should be an integer')
        return
    
    stock = twstock.Stock(stock_code)
    ma_31 = stock.moving_average(
        data=stock.price, 
        days=int(days)
    )

    await ctx.send(message.ma31(ma_31, days))

client.run(DC_Token)