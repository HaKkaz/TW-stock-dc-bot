from unittest.mock import patch, Mock
import logger
import importlib


def test_channel_log():
    mock_ctx = Mock()
    mock_ctx.channel.id = 12345
    mock_ctx.channel.name = 'test-channel'

    log_message = logger.channel_log(mock_ctx)
    assert log_message == 'command - 12345 - test-channel - '


def test_logger_setup():
    with patch('os.path.exists', return_value=False), \
            patch('os.makedirs') as mock_makedirs, \
            patch('logging.FileHandler') as mock_file_handler:
        importlib.reload(logger)

    mock_makedirs.assert_called_once_with('log')
    mock_file_handler.assert_called_once_with(
        filename='log/discord.log',
        encoding='utf-8',
        mode='a'
    )
