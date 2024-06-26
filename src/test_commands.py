import pytest
from unittest.mock import patch, AsyncMock, mock_open
import commands
import os


# test price command
@pytest.mark.asyncio
@patch('twstock.realtime.get')
async def test_price_command_success(mock_get):
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


@pytest.mark.asyncio
@patch('twstock.realtime.get')
async def test_price_command_failure(mock_get):
    mock_get.return_value = {
        'success': False,
        'rtmessage': 'Invalid stock code'
    }

    ctx = AsyncMock()
    ctx.send = AsyncMock()

    await commands.price(ctx, '2330')
    ctx.send.assert_called_with('error: Invalid stock code')


# test ma31 command
@pytest.mark.asyncio
async def test_ma31_command_invalid_days():
    ctx = AsyncMock()
    ctx.send = AsyncMock()

    await commands.ma31(ctx, '2330', 'invalid_days')
    ctx.send.assert_called_with('days should be an integer')


@pytest.mark.asyncio
async def test_ma31_command_invalid_stock_code():
    ctx = AsyncMock()
    ctx.send = AsyncMock()

    invalid_stock_code = '0000'  # 假設這個股票代碼不存在
    with patch('twstock.codes', new={}):
        await commands.ma31(ctx, invalid_stock_code, '10')
    ctx.send.assert_called_with('該股票不存在')


@pytest.mark.asyncio
@patch('twstock.Stock')
async def test_ma31_command_success(mock_stock):
    ctx = AsyncMock()
    ctx.send = AsyncMock()

    # 模擬移動平均線
    mock_stock.return_value.moving_average.return_value = [100, 105, 110]

    await commands.ma31(ctx, '2330', '3')
    ctx.send.assert_called_with('31 日內的 3MA:\n[100, 105, 110]')


# test best4Buy command
@pytest.mark.asyncio
async def test_best4Buy_command_invalid_stock_code():
    ctx = AsyncMock()
    ctx.send = AsyncMock()

    invalid_stock_code = '0000'
    with patch('twstock.codes', new={}):
        await commands.best4Buy(ctx, invalid_stock_code)
    ctx.send.assert_called_with('該股票不存在')


@pytest.mark.asyncio
@patch('twstock.Stock')
@patch('twstock.BestFourPoint')
async def test_best4Buy_command_success(mock_bfp, mock_stock):
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
@pytest.mark.asyncio
async def test_best4Sell_command_invalid_stock_code():
    ctx = AsyncMock()
    ctx.send = AsyncMock()

    invalid_stock_code = '0000'
    with patch('twstock.codes', new={}):
        await commands.best4Sell(ctx, invalid_stock_code)
    ctx.send.assert_called_with('該股票不存在')


@pytest.mark.asyncio
@patch('twstock.Stock')
@patch('twstock.BestFourPoint')
async def test_best4Sell_command_success(mock_bfp, mock_stock):
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
@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open, read_data="")
@patch("os.path.exists", return_value=False)
@patch("os.makedirs")
async def test_subscribe_command_first_time(
    mock_makedirs, mock_exists, mock_open
):
    ctx = AsyncMock()
    ctx.send = AsyncMock()

    await commands.subscribe(ctx)
    ctx.send.assert_called_with('Subscribe successfully.')
    assert mock_open.call_count == 3  # open is called multiple times
    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'w')
    mock_open().write.assert_any_call(f"{ctx.channel.id}\n")
    mock_makedirs.assert_called_once_with('subscribe')
    mock_exists.assert_called()


@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open, read_data="12345\n67890\n")
@patch("os.path.exists", return_value=True)
async def test_subscribe_command_already_subscribed(mock_exists, mock_open):
    ctx = AsyncMock()
    ctx.send = AsyncMock()
    ctx.channel.id = 12345

    await commands.subscribe(ctx)
    ctx.send.assert_called_with('Already subscribed.')
    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'r')


# Test unsubscribe command
@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open, read_data="12345\n67890\n")
@patch("os.path.exists", return_value=True)
async def test_unsubscribe_command_success(
    mock_exists, mock_open
):
    ctx = AsyncMock()
    ctx.send = AsyncMock()
    ctx.channel.id = 12345

    await commands.unsubscribe(ctx)
    ctx.send.assert_called_with('Unsubscribe successfully.')
    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'r')
    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'w')
    mock_open().write.assert_called_with("67890\n")


@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open)
@patch("os.path.exists", side_effect=lambda path: path !=
       os.path.join('subscribe', 'subscriber.txt') and path != 'subscribe')
@patch("os.makedirs")
async def test_unsubscribe_command_not_subscribed(
    mock_makedirs, mock_exists, mock_open
):
    ctx = AsyncMock()
    ctx.send = AsyncMock()
    ctx.channel.id = 12345

    await commands.unsubscribe(ctx)

    mock_makedirs.assert_called_once_with('subscribe')

    # check that the file is created with empty subscription
    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'w')
    mock_open().write.assert_any_call('')
    mock_open.assert_any_call(os.path.join('subscribe', 'subscriber.txt'), 'r')
    ctx.send.assert_called_with('Already unsubscribed.')
