from bot import LOGGER


def process_message(channel, method, properties, body):
    """
    Method should process messages for bot from message broker and trigger
    events on bot's side:
    - datemaker sends a list of events to user
    - datemaker sends an event registration confirmation request
    :param channel:
    :param method:
    :param properties:
    :param body:
    :return:
    """
    LOGGER.info(f'Got message: channel={channel}, method={method}, '
                f'properties={properties}, body={body}')
