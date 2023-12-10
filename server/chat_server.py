import asyncio
import json

import logging

import websockets

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
logger.debug('Logger initiated!')

clients = {}  # remake to redis?


async def handle_client(websocket: websockets.WebSocketClientProtocol):
    """
    Protocol of client handling.
    First message from client should be dict containing username and text "connecting".
    Server responds with "connected".
    After that messaging can be made.
    System commands must be sent in key "command".

    Examples of messages:
    {"username": "Ivan", "message": "connecting"} # from client who wants to connect
    {"message": "hello"} # regular message from client
    {"command": "room switch 2"} # command to switch room (for future)
    """
    to_run = True
    while to_run:
        try:
            client = websocket.remote_address
            data = await websocket.recv()
            message = json.loads(data)
        except websockets.ConnectionClosedOK:
            if client in clients.keys():
                del clients[client]
                logger.debug(f'Client {client} disconnected')
            continue

        except Exception as e:
            logger.warning(f'Caught error: {e}')
            continue

        if client in clients.keys():
            await handle_messaging(websocket, message)
            await handle_commands()
            await handle_system()
        else:
            await connect_user_to_chat(websocket, message)


async def connect_user_to_chat(websocket: websockets.WebSocketClientProtocol, message: dict):
    try:
        username = message['username']
        if message['message'] == 'connecting':
            logger.debug(f'User {username} connected')
        else:
            logger.warning('No connecting message, dropping')
    except KeyError:
        logger.warning('Bad connect message got from user, dropping')
    finally:
        logger.debug(message)

    await websocket.send(json.dumps({'system': 'connected'}))
    for client in clients.values():
        client.send('Another user connected!')

    clients[websocket.remote_address] = websocket


async def handle_commands():
    pass


async def handle_system():
    pass


async def handle_messaging(websocket: websockets.WebSocketClientProtocol, message: dict):
    try:
        message = message['message']
    except KeyError:
        return

    logger.debug(f'{websocket.remote_address}: {message}')

    # broadcasting?
    for client, ws in clients.items():
        if ws != websocket:
            ws.send(f'{websocket.remote_address}: {message}')


async def main():
    async with websockets.serve(handle_client, "localhost", 4321) as server:
        await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())
