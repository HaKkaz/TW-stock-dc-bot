import pytest
from unittest.mock import patch, AsyncMock, mock_open
import commands
import os


# test price command
# Variables: stock['success']
'''
CC: stock_code(true)
'''
@pytest.mark.asyncio
@patch('twstock.realtime.get')
async def test_price_command_valid_stock_code(mock_get):
    mock_get.return_value = {
        'success': True,
        'realtime': {'latest_trade_price': '123.45'},
        'info': {'name': 'Test Stock'}
    }

    # 模擬 Discord 的 ctx
    ctx = AsyncMock()
    ctx.send = AsyncMock()

    await commands.price(ctx, '2330')
    ctx.send.assert_called_with('Test Stock\n目前價格: 123.45')


'''
CC: stock_code(false)
'''
@pytest.mark.asyncio
@patch('twstock.realtime.get')
async def test_price_command_invalid_stock_code(mock_get):
    mock_get.return_value = {
        'success': False,
        'rtmessage': 'Invalid stock code'
    }

    ctx = AsyncMock()
    ctx.send = AsyncMock()

    await commands.price(ctx, '2330')
    ctx.send.assert_called_with('error: Invalid stock code')


# test ma31 command
# Variables: stock_code, days
'''
CC : days(false)
'''
@pytest.mark.asyncio
async def test_ma31_command_invalid_days():
    ctx = AsyncMock()
    ctx.send = AsyncMock()

    await commands.ma31(ctx, '2330', 'invalid_days')
    ctx.send.assert_called_with('days should be an integer')


'''
CC : days(true)
'''
@pytest.mark.asyncio
@patch('twstock.codes', new={'2330': '台積電'})
@patch('twstock.Stock')
async def test_ma31_command_valid_days(mock_stock):
    ctx = AsyncMock()
    ctx.send = AsyncMock()

    await commands.ma31(ctx, '0000', '10')
    ctx.send.assert_called_with('該股票不存在')


'''
CC : stock_code in twstock.codes(false)
'''
@pytest.mark.asyncio
async def test_ma31_command_invalid_stock_code():
    ctx = AsyncMock()
    ctx.send = AsyncMock()

    invalid_stock_code = '0000'  # 假設這個股票代碼不存在
    with patch('twstock.codes', new={}):
        await commands.ma31(ctx, invalid_stock_code, '10')
    ctx.send.assert_called_with('該股票不存在')


'''
CC : stock_code in twstock.codes(true)
'''
@pytest.mark.asyncio
@patch('twstock.codes', new={'2330': '台積電'})
@patch('twstock.Stock')
async def test_ma31_command_valid_stock_code(mock_stock):
    ctx = AsyncMock()
    ctx.send = AsyncMock()

    mock_stock.return_value.price = [100, 105, 110]
    mock_stock.return_value.moving_average.return_value = [102, 103, 104]

    await commands.ma31(ctx, '2330', '3')
    ctx.send.assert_called_with('31 日內的 3MA:\n[102, 103, 104]')


# test best4Buy command
# variable: stock_code
'''
CC : stock_code in twstock.codes(false)
'''
@pytest.mark.asyncio
async def test_best4Buy_command_invalid_stock_code():
    ctx = AsyncMock()
    ctx.send = AsyncMock()

    invalid_stock_code = '0000'
    with patch('twstock.codes', new={}):
        await commands.best4Buy(ctx, invalid_stock_code)
    ctx.send.assert_called_with('該股票不存在')


'''
CC : stock_code in twstock.codes(true)
'''
@pytest.mark.asyncio
@patch('twstock.Stock')
@patch('twstock.BestFourPoint')
async def test_best4Buy_command_valid_stock_code(mock_bfp, mock_stock):
    ctx = AsyncMock()
    ctx.send = AsyncMock()

    mock_stock.return_value.capacity = [100, 200]
    mock_stock.return_value.price = [50, 60]
    mock_stock.return_value.open = [55, 65]

    # mock BestFourPoint
    mock_bfp.return_value.best_four_point_to_buy.return_value = 'Best to Buy'
    mock_bfp.return_value.best_buy_1.return_value = True
    mock_bfp.return_value.best_buy_2.return_value = False
    mock_bfp.return_value.best_buy_3.return_value = False
    mock_bfp.return_value.best_buy_4.return_value = False

    await commands.best4Buy(ctx, '2330')
    ctx.send.assert_called_with('2330 Best to Buy')


# test best4Sell command
# variable: stock_code
'''
CC : stock_code in twstock.codes(false)
'''
@pytest.mark.asyncio
async def test_best4Sell_command_invalid_stock_code():
    ctx = AsyncMock()
    ctx.send = AsyncMock()

    invalid_stock_code = '0000'
    with patch('twstock.codes', new={}):
        await commands.best4Sell(ctx, invalid_stock_code)
    ctx.send.assert_called_with('該股票不存在')


'''
CC : stock_code in twstock.codes(true)
'''
@pytest.mark.asyncio
@patch('twstock.Stock')
@patch('twstock.BestFourPoint')
async def test_best4Sell_command_valid_stock_code(mock_bfp, mock_stock):
    ctx = AsyncMock()
    ctx.send = AsyncMock()

    mock_stock.return_value.capacity = [100, 200]
    mock_stock.return_value.price = [60, 50]
    mock_stock.return_value.open = [65, 55]

    mock_bfp.return_value.best_four_point_to_sell.return_value = 'Best to Sell'
    mock_bfp.return_value.best_sell_1.return_value = True
    mock_bfp.return_value.best_sell_2.return_value = False
    mock_bfp.return_value.best_sell_3.return_value = False
    mock_bfp.return_value.best_sell_4.return_value = False

    await commands.best4Sell(ctx, '2330')
    ctx.send.assert_called_with('2330 Best to Sell')


# Test subscribe command
# variable: exists(folder_path)、exists(file_path)、channel_id(in existing_ids)
'''
CC : folder_path does not exist (true)
'''
@pytest.mark.asyncio
@patch("os.path.exists")
@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open, read_data="")
async def test_subscribe_folder_not_exist(mock_open, mock_makedirs, mock_exists):
    ctx = AsyncMock()
    ctx.channel.id = 123

    # Mock return values for os.path.exists
    mock_exists.side_effect = lambda x: False if x == 'subscribe' else True

    await commands.subscribe(ctx)

    mock_makedirs.assert_called_once_with('subscribe')
    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'a')
    ctx.send.assert_called_with('Subscribe successfully.')


'''
CC : folder_path does not exist (false)
'''
@pytest.mark.asyncio
@patch("os.path.exists", return_value=True)
@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open, read_data="")
async def test_subscribe_folder_exist(mock_open, mock_makedirs, mock_exists):
    ctx = AsyncMock()
    ctx.channel.id = 123

    await commands.subscribe(ctx)

    mock_makedirs.assert_not_called()
    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'r')
    ctx.send.assert_called_with('Subscribe successfully.')


'''
CC : file_path does not exist (true)
'''
@pytest.mark.asyncio
@patch("os.path.exists", side_effect=lambda x: x != os.path.join('subscribe', 'subscriber.txt'))
@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open, read_data="")
async def test_subscribe_file_not_exist(mock_open, mock_makedirs, mock_exists):
    ctx = AsyncMock()
    ctx.channel.id = 123

    await commands.subscribe(ctx)

    mock_makedirs.assert_not_called()
    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'w')
    ctx.send.assert_called_with('Subscribe successfully.')


'''
CC : file_path does not exist (false)
'''
@pytest.mark.asyncio
@patch("os.path.exists", return_value=True)
@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open, read_data="123\n456")
async def test_subscribe_file_exist(mock_open, mock_makedirs, mock_exists):
    ctx = AsyncMock()
    ctx.channel.id = 789

    await commands.subscribe(ctx)

    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'r')
    ctx.send.assert_called_with('Subscribe successfully.')


'''
CC : channel_id in existing ids (true)
'''
@pytest.mark.asyncio
@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data="123\n456")
async def test_subscribe_channel_id_in_existing_ids(mock_open, mock_exists):
    ctx = AsyncMock()
    ctx.channel.id = 123

    await commands.subscribe(ctx)

    ctx.send.assert_called_with('Already subscribed.')


'''
CC : channel_id in existing ids (false)
'''
@pytest.mark.asyncio
@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data="456\n789")
async def test_subscribe_channel_id_not_in_existing_ids(mock_open, mock_exists):
    ctx = AsyncMock()
    ctx.channel.id = 123

    await commands.subscribe(ctx)

    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'a')
    ctx.send.assert_called_with('Subscribe successfully.')


# Test unsubscribe command
# variables: folder_path, file_path, channel_id(in existing_ids)

'''
CC : folder_path does not exist (true)
'''
@pytest.mark.asyncio
@patch("os.path.exists")
@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open, read_data="")
async def test_unsubscribe_folder_not_exist(mock_open, mock_makedirs, mock_exists):
    ctx = AsyncMock()
    ctx.channel.id = 123

    # Mock return values for os.path.exists
    mock_exists.side_effect = lambda x: False if x == 'subscribe' else True

    await commands.unsubscribe(ctx)

    mock_makedirs.assert_called_once_with('subscribe')
    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'r')
    ctx.send.assert_called_with('Already unsubscribed.')


'''
CC : folder_path does not exist (false)
'''
@pytest.mark.asyncio
@patch("os.path.exists", return_value=True)
@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open, read_data="")
async def test_unsubscribe_folder_exist(mock_open, mock_makedirs, mock_exists):
    ctx = AsyncMock()
    ctx.channel.id = 123

    await commands.unsubscribe(ctx)

    mock_makedirs.assert_not_called()
    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'r')
    ctx.send.assert_called_with('Already unsubscribed.')


'''
CC : file_path does not exist (true)
'''
@pytest.mark.asyncio
@patch("os.path.exists", side_effect=lambda x: x != os.path.join('subscribe', 'subscriber.txt'))
@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open, read_data="")
async def test_unsubscribe_file_not_exist(mock_open, mock_makedirs, mock_exists):
    ctx = AsyncMock()
    ctx.channel.id = 123

    await commands.unsubscribe(ctx)

    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'w')
    ctx.send.assert_called_with('Already unsubscribed.')


'''
CC : file_path does not exist (false)
'''
@pytest.mark.asyncio
@patch("os.path.exists", return_value=True)
@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open, read_data="123\n456")
async def test_unsubscribe_file_exist(mock_open, mock_makedirs, mock_exists):
    ctx = AsyncMock()
    ctx.channel.id = 789

    await commands.unsubscribe(ctx)

    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'r')
    ctx.send.assert_called_with('Already unsubscribed.')


'''
CC : channel_id in existing ids (true)
'''
@pytest.mark.asyncio
@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data="123\n456")
async def test_unsubscribe_channel_id_in_existing_ids(mock_open, mock_exists):
    ctx = AsyncMock()
    ctx.channel.id = 123

    await commands.unsubscribe(ctx)

    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'w')
    ctx.send.assert_called_with('Unsubscribe successfully.')


'''
CC : channel_id in existing ids (false)
'''
@pytest.mark.asyncio
@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data="456\n789")
async def test_unsubscribe_channel_id_not_in_existing_ids(mock_open, mock_exists):
    ctx = AsyncMock()
    ctx.channel.id = 123

    await commands.unsubscribe(ctx)

    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'r')
    ctx.send.assert_called_with('Already unsubscribed.')