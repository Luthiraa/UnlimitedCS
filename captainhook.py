import os
import base64
import requests
import json
import webhooks

WEBHOOK_URL = webhooks.webhook_urls[0]

# 8MB :(((( mfs reduced max file size aghain bru
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
#chunk is within Ddscord's limit for description

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

def upload_file(file_path):
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    total_chunks = (file_size // CHUNK_SIZE) + 1

    for index, chunk in enumerate(split_file(file_path)):
        encoded_chunk = encode_chunk(chunk)
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
    print("Webhook Messages:", webhook_messages)  # Debugging statement
    for message in webhook_messages:
        if isinstance(message, dict) and f"File: {file_name}" in message.get('content', ''):
            chunk = base64.b64decode(message['embeds'][0]['description'])
            file_chunks.append(chunk)
    
    with open(save_path, "wb") as f:
        for chunk in file_chunks:
            f.write(chunk)
    print(f"File {file_name} downloaded successfully.")


# upload file
# upload_file("test.jpg")

# download file
webhook_messages = get_webhook_messages()
download_file(webhook_messages, "test.jpg", "downloaded_test.jpg")