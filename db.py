import os
import json
import discord
from discord.ext import commands
import webhooks
# Discord bot token and channel ID
DISCORD_BOT_TOKEN = webhooks.webhooks[1]
CHANNEL_ID = webhooks.webhooks[2]
CHUNK_SIZE = 8 * 1024 * 1024

# Define the intents
intents = discord.Intents.default()
intents.messages = True  # Enable the message intents

bot = commands.Bot(command_prefix='!', intents=intents)

def split_file(file_path):
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            yield chunk

async def send_chunk(channel, chunk, file_name, chunk_index, total_chunks):
    payload = {
        "content": f"File: {file_name}, Chunk: {chunk_index + 1}/{total_chunks}",
        "embeds": [
            {
                "description": chunk.hex()[:2048]  # Convert bytes to hex string
            }
        ]
    }
    payload_str = json.dumps(payload)
    if len(payload_str) > 6000:
        raise Exception(f"Payload size exceeds Discord's limit for chunk {chunk_index + 1}")

    await channel.send(content=payload["content"], embed=discord.Embed(description=payload["embeds"][0]["description"]))

async def upload_file(channel, file_path):
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    total_chunks = (file_size // CHUNK_SIZE) + 1

    print(f"Uploading file: {file_name}")
    print(f"File size: {file_size} bytes")
    print(f"Total chunks: {total_chunks}")

    for index, chunk in enumerate(split_file(file_path)):
        print(f"Sending chunk {index + 1}/{total_chunks}")
        print(f"Chunk size: {len(chunk)} bytes")
        await send_chunk(channel, chunk, file_name, index, total_chunks)
    print(f"File {file_name} uploaded successfully.")

async def download_file(channel, file_name, save_path):
    messages = []
    async for message in channel.history(limit=100):  # Adjust the limit as needed
        messages.append(message)
    
    file_chunks = []
    
    print(f"Total messages retrieved: {len(messages)}")
    for message in messages:
        if isinstance(message.content, str) and f"File: {file_name}" in message.content:
            try:
                chunk_index = int(message.content.split('Chunk: ')[1].split('/')[0]) - 1
                embed = message.embeds[0].description
                chunk = bytes.fromhex(embed)  # Convert hex string back to bytes
                file_chunks.append((chunk_index, chunk))
                print(f"Decoded chunk {chunk_index + 1} successfully.")
            except Exception as e:
                print(f"Failed to decode chunk: {e}")

    if not file_chunks:
        print(f"No chunks found for file {file_name}.")
        return

    file_chunks.sort(key=lambda x: x[0])

    with open(save_path, "wb") as f:
        for index, (_, chunk) in enumerate(file_chunks):
            print(f"Writing chunk {index + 1} to file.")
            f.write(chunk)
    print(f"File {file_name} downloaded successfully.")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    channel = bot.get_channel(int(CHANNEL_ID))

    # Upload file example
    # await upload_file(channel, "test.jpg")

    # Download file example
    await download_file(channel, "test.jpg", "test_new.jpg")

bot.run(DISCORD_BOT_TOKEN)