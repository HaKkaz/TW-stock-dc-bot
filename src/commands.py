import twstock
import message
import os
from logger import logger, channel_log
from discord.ext import commands

@commands.command()
async def price(ctx, stock_code: str):
    """ 
     [stock_code]: 取得指定股票的即時價格
    """
    stock = twstock.realtime.get(stock_code)
    if stock['success']:
        await ctx.send(message.price_message(stock))
    else:
        await ctx.send('error: ' + stock['rtmessage'])
    logger.info(f'command - {ctx.channel.id} - {ctx.channel.name} - price - {stock_code}')

@commands.command()
async def ma31(ctx, stock_code: str, days: str):
    """ 
    [stock_code] [days]: 取得指定股票的 31 日內指定天數的移動平均線
    """
    try:
        int(days)
    except ValueError:
        await ctx.send('days should be an integer')
        return
    
    if stock_code not in twstock.codes:
        await ctx.send('該股票不存在')
        return

    stock = twstock.Stock(stock_code)
    ma_31 = stock.moving_average(
        data=stock.price, 
        days=int(days)
    )

    await ctx.send(message.ma31(ma_31, days))
    logger.info(channel_log(ctx) + f'ma31 - {stock_code} - {days}')

@commands.command()
async def best4Buy(ctx, stock_code: str):
    """ 
    [stock_code]: 查看指定股票是否正在最佳四大買點
    """
    if stock_code not in twstock.codes:
        await ctx.send('該股票不存在')
        return

    stock = twstock.Stock(stock_code)
    bfp = twstock.BestFourPoint(stock)
    result = bfp.best_four_point_to_buy()
    await ctx.send(f'{stock_code} {result}')
    logger.info(channel_log(ctx) + f'best4Buy - {stock_code}')

@commands.command()
async def best4Sell(ctx, stock_code: str):
    """ 
    [stock_code]: 查看指定股票是否正在最佳四大賣點
    """
    if stock_code not in twstock.codes:
        await ctx.send('該股票不存在')
        return

    stock = twstock.Stock(stock_code)
    bfp = twstock.BestFourPoint(stock)
    result = bfp.best_four_point_to_sell()
    await ctx.send(f'{stock_code} {result}')
    logger.info(channel_log(ctx) + f'best4Sell - {stock_code}')

@commands.command()
async def subscribe(ctx):
    """
    : 訂閱機器人的通知
    """
    # check if the file is exist or not
    folder_path = 'subscribe'
    file_path = os.path.join(folder_path, 'subscriber.txt')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write('')

    with open(file_path, 'r') as file:
        existing_ids = file.read().splitlines()
    
    channel_id: str = str(ctx.channel.id)
    
    if channel_id not in existing_ids:
        with open(file_path, 'a') as file:
            file.write(channel_id + '\n')
        await ctx.send(f'Subscribe successfully.')
        logger.info(channel_log(ctx) + 'subscribe successfully')
    else:
        await ctx.send(f'Already subscribed.')
        logger.info(channel_log(ctx) + 'subscribe already subscribed')