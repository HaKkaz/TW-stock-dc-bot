import logging
import os

# Set the logger
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

# Set log file path
if not os.path.exists('log'):
    os.makedirs('log')
log_file_path = 'log/discord.log'

# Set the log handler
handler = logging.FileHandler(
    filename=log_file_path,
    encoding='utf-8',
    mode='a'
)
handler.setFormatter(
    logging.Formatter(
        '%(asctime)s:%(levelname)s:%(name)s: %(message)s'
    )
)
logger.addHandler(handler)


def channel_log(ctx) -> str:
    return f'command - {ctx.channel.id} - {ctx.channel.name} - '
