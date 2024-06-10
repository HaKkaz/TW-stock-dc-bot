import pytest
from unittest.mock import patch, AsyncMock, mock_open
import commands
import os


# test price command
'''
Variables: stock
Flow of control: stock['success'](true) -> function
For PC、CC、CACC => 2 test cases have to be tested
'''
# stock['success'](true)
@pytest.mark.asyncio
@patch('twstock.realtime.get')
async def test_price_command_stock_false(mock_get):
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


# stock['success'](false)
@pytest.mark.asyncio
@patch('twstock.realtime.get')
async def test_price_command_stock_true(mock_get):
    mock_get.return_value = {
        'success': False,
        'rtmessage': 'Invalid stock code'
    }

    ctx = AsyncMock()
    ctx.send = AsyncMock()

    await commands.price(ctx, '2330')
    ctx.send.assert_called_with('error: Invalid stock code')


# test ma31 command
'''
Variables: stock_code, days
There are two separate predicate 
Flow of control: days(true) -> stock_code in twstock.codes(ture) -> function
For PC、CC are some cases where the predicate is separated
PC、CC、CACC: can be satisfied by testing 2 x 2 = 4 test
Case[days(false)、stock_code in twstock.codes(false)] belongs to Case[days(false)]
4 - 1 = 3 test cases have to be tested
'''
# days(false)
@pytest.mark.asyncio
async def test_ma31_command_days_false():
    ctx = AsyncMock()
    ctx.send = AsyncMock()

    await commands.ma31(ctx, '2330', 'invalid_days')
    ctx.send.assert_called_with('days should be an integer')


# days(true)、stock_code in twstock.codes(false)
@pytest.mark.asyncio
async def test_ma31_command_stock_code_false():
    ctx = AsyncMock()
    ctx.send = AsyncMock()

    invalid_stock_code = '0000'  # 假設這個股票代碼不存在
    with patch('twstock.codes', new={}):
        await commands.ma31(ctx, invalid_stock_code, '10')
    ctx.send.assert_called_with('該股票不存在')


# days(true)、stock_code in twstock.codes(true)
@pytest.mark.asyncio
@patch('twstock.Stock')
async def test_ma31_command_stock_code_true(mock_stock):
    ctx = AsyncMock()
    ctx.send = AsyncMock()

    # 模擬移動平均線
    mock_stock.return_value.moving_average.return_value = [100, 105, 110]

    await commands.ma31(ctx, '2330', '3')
    ctx.send.assert_called_with('31 日內的 3MA:\n[100, 105, 110]')


# test best4Buy command
'''
Variables: stock_code
Flow of control: stock_code(true) -> function
For PC、CC、CACC => 2 test cases have to be tested
'''
# stock_code in twstock.codes(false)
@pytest.mark.asyncio
async def test_best4Buy_command_stock_code_false():
    ctx = AsyncMock()
    ctx.send = AsyncMock()

    invalid_stock_code = '0000'
    with patch('twstock.codes', new={}):
        await commands.best4Buy(ctx, invalid_stock_code)
    ctx.send.assert_called_with('該股票不存在')


@pytest.mark.asyncio
@patch('twstock.Stock')
@patch('twstock.BestFourPoint')
async def test_best4Buy_command_stock_code_true(mock_bfp, mock_stock):
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
'''
Variables: stock_code
Flow of control: stock_code(true) -> function
For PC、CC、CACC => 2 test cases have to be tested
'''
# stock_code in twstock.codes(false)
@pytest.mark.asyncio
async def test_best4Sell_command_stock_code_false():
    ctx = AsyncMock()
    ctx.send = AsyncMock()

    invalid_stock_code = '0000'
    with patch('twstock.codes', new={}):
        await commands.best4Sell(ctx, invalid_stock_code)
    ctx.send.assert_called_with('該股票不存在')


@pytest.mark.asyncio
@patch('twstock.Stock')
@patch('twstock.BestFourPoint')
async def test_best4Sell_command_stock_code_true(mock_bfp, mock_stock):
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
'''
Variable: folder_path_exists[A]、file_path_exists[B]、channel_id in existing_ids[C]
Flow of control: 
    folder_path_exists(false):
        -> Create folder
        file_path_exists(false):
            -> Create file
            channel_id in existing_ids(false)
                -> Subscribe successfully - 1
    folder_path_exists(true):
        file_path_exists(false):
            -> Create file
            channel_id in existing_ids(false)
                -> Subscribe successfully - 2
        file_path_exists(true):
            channel_id in existing_ids(false)
                -> Subscribe successfully - 3
            channel_id in existing_ids(true)
                -> Already subscribed - 4

There are 3 separate predicate and only four valid path
For PC、CC、CACC these four cases should be tested
(they could be tested together because they are independent)
If we took these three cases as one predicate 
=> equal to (A and B and C): Already subscribed、Otherwise: Subscribe successfully
What's more: (C -> B) and (B -> A)
'''
# Case 1: folder_path_exists(false) -> file_path_exists(false) -> channel_id in existing_ids(false)
@pytest.mark.asyncio
@patch("os.path.exists")
@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open, read_data="")
async def test_subscribe_create_folder_and_file(mock_open, mock_makedirs, mock_exists):
    ctx = AsyncMock()
    ctx.channel.id = 123
    ctx.channel.name = 'test_channel'

    # Mock return values for os.path.exists
    mock_exists.side_effect = lambda x: False if x in ['subscribe', os.path.join('subscribe', 'subscriber.txt')] else True

    await commands.subscribe(ctx)

    mock_makedirs.assert_called_once_with('subscribe')
    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'w')
    ctx.send.assert_called_with('Subscribe successfully.')


# Case 2: folder_path_exists(true) -> file_path_exists(false) -> channel_id in existing_ids(false)
@pytest.mark.asyncio
@patch("os.path.exists", side_effect=lambda x: True if x == 'subscribe' else False)
@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open, read_data="")
async def test_subscribe_create_file(mock_open, mock_makedirs, mock_exists):
    ctx = AsyncMock()
    ctx.channel.id = 123
    ctx.channel.name = 'test_channel'

    await commands.subscribe(ctx)

    mock_makedirs.assert_not_called()
    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'w')
    ctx.send.assert_called_with('Subscribe successfully.')


# Case 3: folder_path_exists(true) -> file_path_exists(true) -> channel_id in existing_ids(false)
@pytest.mark.asyncio
@patch("os.path.exists", return_value=True)
@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open, read_data="")
async def test_subscribe_channel_id_not_in_existing_ids(mock_open, mock_makedirs, mock_exists):
    ctx = AsyncMock()
    ctx.channel.id = 123
    ctx.channel.name = 'test_channel'

    await commands.subscribe(ctx)

    mock_makedirs.assert_not_called()
    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'a')
    ctx.send.assert_called_with('Subscribe successfully.')


# Case 4: folder_path_exists(true) -> file_path_exists(true) -> channel_id in existing_ids(true)
@pytest.mark.asyncio
@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data="123\n456")
async def test_subscribe_channel_id_in_existing_ids(mock_open, mock_exists):
    ctx = AsyncMock()
    ctx.channel.id = 123
    ctx.channel.name = 'test_channel'

    await commands.subscribe(ctx)
    ctx.send.assert_called_with('Already subscribed.')


# Test unsubscribe command
'''
Variable: folder_path_exists[A]、file_path_exists[B]、channel_id in existing_ids[C]
Flow of control: 
    folder_path_exists(false):
        -> Create folder
        file_path_exists(false):
            -> Create file
            channel_id in existing_ids(false)
                -> Already unsubscribed - 1
    folder_path_exists(true):
        file_path_exists(false):
            -> Create file
            channel_id in existing_ids(false)
                -> Already unsubscribed - 2
        file_path_exists(true):
            channel_id in existing_ids(false)
                -> Already unsubscribed - 3
            channel_id in existing_ids(true)
                -> Unsubscribe successfully - 4
There are 3 separate predicate and only four valid path (same as subscribe function)
For PC、CC、CACC these four cases should be tested
(they could be tested together because they are independent)
'''
# Case 1: folder_path_exists(false) -> file_path_exists(false) -> channel_id in existing_ids(false)
@pytest.mark.asyncio
@patch("os.path.exists")
@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open, read_data="")
async def test_unsubscribe_create_folder_and_file(mock_open, mock_makedirs, mock_exists):
    ctx = AsyncMock()
    ctx.channel.id = 123
    ctx.channel.name = 'test_channel'

    # Mock return values for os.path.exists
    mock_exists.side_effect = lambda x: False if x in ['subscribe', os.path.join('subscribe', 'subscriber.txt')] else True

    await commands.unsubscribe(ctx)

    mock_makedirs.assert_called_once_with('subscribe')
    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'w')
    ctx.send.assert_called_with('Already unsubscribed.')


# Case 2: folder_path_exists(true) -> file_path_exists(false) -> channel_id in existing_ids(false)
@pytest.mark.asyncio
@patch("os.path.exists", side_effect=lambda x: x == 'subscribe')
@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open, read_data="")
async def test_unsubscribe_create_file(mock_open, mock_makedirs, mock_exists):
    ctx = AsyncMock()
    ctx.channel.id = 123
    ctx.channel.name = 'test_channel'

    await commands.unsubscribe(ctx)

    mock_makedirs.assert_not_called()
    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'w')
    ctx.send.assert_called_with('Already unsubscribed.')


# Case 3: folder_path_exists(true) -> file_path_exists(true) -> channel_id in existing_ids(false)
@pytest.mark.asyncio
@patch("os.path.exists", return_value=True)
@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open, read_data="")
async def test_unsubscribe_channel_id_not_in_existing_ids(mock_open, mock_makedirs, mock_exists):
    ctx = AsyncMock()
    ctx.channel.id = 123
    ctx.channel.name = 'test_channel'

    await commands.unsubscribe(ctx)

    mock_makedirs.assert_not_called()
    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'r')
    ctx.send.assert_called_with('Already unsubscribed.')


# Case 4: folder_path_exists(true) -> file_path_exists(true) -> channel_id in existing_ids(true)
@pytest.mark.asyncio
@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data="123\n456")
async def test_unsubscribe_channel_id_in_existing_ids(mock_open, mock_exists):
    ctx = AsyncMock()
    ctx.channel.id = 123
    ctx.channel.name = 'test_channel'

    await commands.unsubscribe(ctx)

    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'w')
    ctx.send.assert_called_with('Unsubscribe successfully.')
