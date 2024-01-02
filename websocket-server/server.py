import asyncio
import json
import logging

import websockets

from system_messages import CONNECTED, ANOTHER_USER_CONNECTED, CONNECTING, HEARTBEAT

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
logger.debug('Logger initiated!')

clients = {}  # remake to redis?
# todo: добавить асинхронный луп который проверяет наличие сигналов в очереди сообщений
#   для рассылки уведомлений о начале чата


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
        finally:
            await asyncio.sleep(0.1)

        if client in clients.keys():
            await handle_messaging(websocket, message)
            await handle_commands()
            await handle_system(websocket, message)
        else:
            await connect_user_to_chat(websocket, message)

        await asyncio.sleep(0.1)


async def connect_user_to_chat(websocket: websockets.WebSocketClientProtocol, message: dict):
    try:
        username = message['username']
        if message['system'] == CONNECTING:
            logger.debug(f'User {username} connected')
        else:
            logger.warning('No connecting message, dropping')
    except KeyError:
        logger.warning('Bad connect message got from user, dropping')
    finally:
        logger.debug(message)

    await websocket.send(json.dumps({'system': CONNECTED}))
    for client in clients.values():
        await client.send(json.dumps({'system': ANOTHER_USER_CONNECTED}))

    clients[websocket.remote_address] = websocket


async def handle_commands():
    pass


async def handle_system(websocket: websockets.WebSocketClientProtocol, message: dict):
    try:
        system_message = message['system']
    except KeyError as e:
        return

    logger.debug(f'[SYS] {websocket.remote_address}: {system_message}')

    if system_message == HEARTBEAT:
        await websocket.send(json.dumps({'system': HEARTBEAT}))


async def handle_messaging(websocket: websockets.WebSocketClientProtocol, message: dict):
    try:
        message = message['message']
    except KeyError:
        return

    logger.debug(f'[MSG] {websocket.remote_address}: {message}')

    for client, ws in clients.items():
        if ws != websocket:
            await ws.send(json.dumps({'user': websocket.remote_address, 'message': message}))


async def main():
    async with websockets.serve(handle_client, "localhost", 4321) as server:
        await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())
