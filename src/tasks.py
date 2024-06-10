from discord.ext import tasks
from datetime import datetime, timezone, timedelta, time

# Define the open and close time of Taiwan Stock Market
utc8 = timezone(timedelta(hours=8))
open_time = time(hour = 9, minute = 55, tzinfo = utc8)
close_time = time(hour = 13, minute = 25, tzinfo = utc8)

@tasks.loop(time=open_time)
# @tasks.loop(seconds=60)
async def open_alert_loop(ctx):
    if datetime.now(utc8).weekday() < 5:
        with open('subscribe/subscribe.txt', 'r') as file:
            channel_ids = [line.rstrip() for line in file.readlines()]
            for channel_id in channel_ids:
                channel = await ctx.get_channel(channel_id)
                if channel:
                    await channel.send('再五分鐘開盤啦！')

@tasks.loop(time=close_time)
# @tasks.loop(seconds=60)
async def close_alert_loop(ctx):
    if datetime.now(utc8).weekday() < 5:
        with open('subscribe/subscribe.txt', 'r') as file:
            channel_ids = [line.rstrip() for line in file.readlines()]
            for channel_id in channel_ids:
                channel = await ctx.get_channel(channel_id)
                if channel:
                    await channel.send('再五分鐘收盤啦！') 