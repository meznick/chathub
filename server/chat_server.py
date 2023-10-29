import asyncio
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
logger.debug('Logger initiated!')

clients = {}  # remake to redis?


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    username = await connect_user_to_chat(writer)
    try:
        await handle_messaging(reader, writer, username)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.warning(f'Caught error: {e}')
    finally:
        del clients[username]
        for client_writer in clients.values():
            client_writer.write(f'{username} disconnected'.encode())
            await client_writer.drain()
        writer.close()
        await writer.wait_closed()
        logger.debug(f'{username} disconnected')


async def connect_user_to_chat(writer: asyncio.StreamWriter) -> str:
    host, port = writer.get_extra_info('peername')
    username = f'{host}:{port}'
    logger.debug(f'User {username} connected')
    writer.write(b'You can start chatting')
    await writer.drain()
    for client_writer in clients.values():
        client_writer.write('Another user connected!'.encode())
        await client_writer.drain()
    clients[username] = writer
    return username


async def handle_messaging(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, username: str):
    while True:
        data = await reader.read(100)
        message = data.decode()
        if not message:
            break

        logger.debug(f'{username}: {message.strip()}')

        # broadcasting?
        for client, client_writer in clients.items():
            if client_writer != writer:
                client_writer.write(f'{username}: {message}'.encode())
                await client_writer.drain()


async def main():
    server = await asyncio.start_server(
        handle_client,
        'localhost',
        1234
    )

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
