import socketio
import asyncio

# Standard Python client based on Socket.IO
sio = socketio.AsyncClient()

@sio.event
async def connect():
    print("Connected to the server.")
    asyncio.create_task(send_commands_task())  # Changed from threading to asyncio task

@sio.event
async def disconnect():
    print("Disconnected from the server.")

@sio.event
async def response(data):
    print("Response:", data)

async def send_commands_task():
    while True:
        command = await asyncio.to_thread(input, "Enter command (or type 'exit' to disconnect): ")
        if command.lower() == 'exit':
            await sio.disconnect()
            break
        await sio.emit('process_command', command)

async def start():
    await sio.connect('http://127.0.0.1:5000')
    await sio.wait()

if __name__ == '__main__':
    asyncio.run(start())