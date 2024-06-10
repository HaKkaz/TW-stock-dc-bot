from dotenv import load_dotenv
from logger import logger
from dc_client import client
import os

# Load .env file
load_dotenv(override=True)

# Get the specific environment variable
DC_Token = os.getenv('DC_Token')


# events
@client.event
async def on_ready():
    logger.info('start bot successfully')
    print('start bot successfully')

client.run(DC_Token)
