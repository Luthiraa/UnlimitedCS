import os
import base64
import requests
import json
import webhooks

# Store the webhook in a different file for security and import it
WEBHOOK_URL = webhooks.webhooks[0]
print(f"Webhook URL: {WEBHOOK_URL}")  # Debugging statement

# 8MB :(((( mfs reduced max file size again bru
CHUNK_SIZE = 8 * 1024 * 1024

def split_file(file_path):
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            yield chunk

def encode_chunk(chunk):
    return base64.b64encode(chunk).decode('utf-8')

def send_chunk(encoded_chunk, file_name, chunk_index, total_chunks):
    # Ensure the chunk is within Discord's limit for description
    description = encoded_chunk[:2048]
    payload = {
        "content": f"File: {file_name}, Chunk: {chunk_index + 1}/{total_chunks}",
        "embeds": [
            {
                "description": description
            }
        ]
    }
    payload_str = json.dumps(payload)
    if len(payload_str) > 6000:
        raise Exception(f"Payload size exceeds Discord's limit for chunk {chunk_index + 1}")

    response = requests.post(WEBHOOK_URL, json=payload)
    if response.status_code != 204:
        print(f"Failed to send chunk {chunk_index + 1}")
        print(f"Status Code: {response.status_code}")
        print(f"Response Content: {response.content}")
        raise Exception(f"Failed to send chunk {chunk_index + 1}")
    else:
        print(f"Chunk {chunk_index + 1} sent successfully.")
        print(f"Response Headers: {response.headers}")
        print(f"Response ID: {response.headers.get('X-Discord-Response-ID')}")

def upload_file(file_path):
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    total_chunks = (file_size // CHUNK_SIZE) + 1

    print(f"Uploading file: {file_name}")
    print(f"File size: {file_size} bytes")
    print(f"Total chunks: {total_chunks}")

    for index, chunk in enumerate(split_file(file_path)):
        encoded_chunk = encode_chunk(chunk)
        print(f"Sending chunk {index + 1}/{total_chunks}")
        print(f"Chunk size: {len(chunk)} bytes")
        send_chunk(encoded_chunk, file_name, index, total_chunks)
    print(f"File {file_name} uploaded successfully.")

def get_webhook_messages():
    response = requests.get(WEBHOOK_URL)
    if response.status_code != 200:
        print(f"Failed to retrieve messages")
        print(f"Status Code: {response.status_code}")
        print(f"Response Content: {response.content}")
        raise Exception("Failed to retrieve messages")
    return json.loads(response.content)

def download_file(webhook_messages, file_name, save_path):
    file_chunks = []
    print(f"Total messages retrieved: {len(webhook_messages)}")  # Debugging statement
    for message in webhook_messages:
        print(f"Processing message: {message}")  # Debugging statement
        if isinstance(message, dict) and f"File: {file_name}" in message.get('content', ''):
            try:
                chunk_index = int(message['content'].split('Chunk: ')[1].split('/')[0]) - 1
                encoded_chunk = message['embeds'][0]['description']
                chunk = base64.b64decode(encoded_chunk)
                file_chunks.append((chunk_index, chunk))
                print(f"Decoded chunk {chunk_index + 1} successfully.")
            except Exception as e:
                print(f"Failed to decode chunk: {e}")
    
    if not file_chunks:
        print(f"No chunks found for file {file_name}.")
        return
    
    # Sort chunks by their index to ensure correct order
    file_chunks.sort(key=lambda x: x[0])
    
    # Write the decoded chunks to the file
    with open(save_path, "wb") as f:
        for index, (_, chunk) in enumerate(file_chunks):
            print(f"Writing chunk {index + 1} to file.")
            f.write(chunk)
    print(f"File {file_name} downloaded successfully.")

# Example usage:
# Uploading a file
# upload_file("new.jpg")

# Downloading the file
webhook_messages = get_webhook_messages()
download_file(webhook_messages, "new.jpg", "test_new.jpg")
