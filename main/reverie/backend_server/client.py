import socketio
import asyncio
import threading

# Standard Python client based on Socket.IO
sio = socketio.AsyncClient()
stop_thread = False

@sio.event
async def connect():
    print("Connected to the server.")
    threading.Thread(target=send_commands_thread, daemon=True).start()

@sio.event
async def disconnect():
    print("Disconnected from the server.")
    global stop_thread
    stop_thread = True

@sio.event
async def response(data):
    print("Response:", data)

def send_commands_thread():
    global stop_thread
    while not stop_thread:
        command = input("Enter command (or type 'exit' to disconnect): ")
        if command.lower() == 'exit':
            asyncio.run(sio.disconnect())
            break
        asyncio.run(sio.emit('process_command', command))

async def start():
    await sio.connect('http://127.0.0.1:5000')
    await sio.wait()

if __name__ == '__main__':
    asyncio.run(start())
