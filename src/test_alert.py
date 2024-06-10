import pytest
from unittest.mock import patch, mock_open, AsyncMock
from datetime import datetime
from tasks import open_alert_loop, close_alert_loop, utc8

@pytest.mark.asyncio
@patch('builtins.open', new_callable=mock_open, read_data='123456789\n987654321')
@patch('tasks.datetime')
async def test_open_alert_loop(mock_datetime, mock_open_func):
    # Mock datetime to return a weekday
    mock_datetime.now.return_value = datetime(2024, 6, 10, 9, 50, tzinfo=utc8)
    mock_ctx = AsyncMock()
    mock_channel = AsyncMock()
    mock_channel.send.return_value = AsyncMock()  # Ensure that send returns an awaitable object
    mock_ctx.get_channel.return_value = mock_channel

    await open_alert_loop(mock_ctx)

    mock_open_func.assert_called_once_with('subscribe/subscribe.txt', 'r')
    mock_ctx.get_channel.assert_any_call('123456789')
    mock_ctx.get_channel.assert_any_call('987654321')
    mock_channel.send.assert_called_with('再五分鐘開盤啦！')

@pytest.mark.asyncio
@patch('builtins.open', new_callable=mock_open, read_data='123456789\n987654321')
@patch('tasks.datetime')
async def test_close_alert_loop(mock_datetime, mock_open_func):
    # Mock datetime to return a weekday
    mock_datetime.now.return_value = datetime(2024, 6, 10, 13, 20, tzinfo=utc8)

    mock_ctx = AsyncMock()
    mock_channel = AsyncMock()
    mock_channel.send.return_value = AsyncMock()  # Ensure that send returns an awaitable object
    mock_ctx.get_channel.return_value = mock_channel

    await close_alert_loop(mock_ctx)

    mock_open_func.assert_called_once_with('subscribe/subscribe.txt', 'r')
    mock_ctx.get_channel.assert_any_call('123456789')
    mock_ctx.get_channel.assert_any_call('987654321')
    mock_channel.send.assert_called_with('再五分鐘收盤啦！')
