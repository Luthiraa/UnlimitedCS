import discord
from discord.ext import commands
import aiohttp
import os
import webhooks

TOKEN = webhooks.webhooks[1]
CHANNEL_ID = int((webhooks.webhooks[2]))

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

async def upload_file(file_path: str):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        with open(file_path, 'rb') as file:
            await channel.send(file=discord.File(file, os.path.basename(file_path)))
        print('File uploaded successfully.')
    else:
        print('Channel not found.')

async def download_file(message_id: int, save_path: str):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        try:
            message = await channel.fetch_message(message_id)
            if message.attachments:
                attachment = message.attachments[0]
                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment.url) as response:
                        if response.status == 200:
                            with open(save_path, 'wb') as file:
                                file.write(await response.read())
                            print('File downloaded successfully.')
                        else:
                            print(f'Failed to download file. HTTP status: {response.status}')
            else:
                print('No attachments found in the message.')
        except discord.errors.NotFound:
            print(f'Message with ID {message_id} not found.')
    else:
        print('Channel not found.')

# Example usage
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # await upload_file('test.jpg')  # Replace with your file path
    await download_file(1270576014363459645, 'test11111.jpg')  # Replace with your message ID and save path

bot.run(TOKEN)