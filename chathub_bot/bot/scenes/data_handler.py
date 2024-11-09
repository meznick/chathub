from collections.abc import Callable
from functools import wraps
from typing import Dict, List, Optional


async def manage_waiting_list(func):
    data_handler = DataHandler()

    @wraps
    async def wrapper(self, *args, **kwargs):
        chat_id = kwargs['chat_id']
        message_id = kwargs['message_id']
        try:
            result = await func(*args, **kwargs)
            data_handler.delete_from_waiting(chat_id, message_id)
        except:
            result = False
        finally:
            return result
    return wrapper


class DataHandler:
    """
    Class for handling data from message broker.
    """
    waiting: Dict[str, Callable] = {}

    def wait_for_data(self, chat_id, message_id, handler):
        self.waiting.update({
            f'{chat_id}_{message_id}': handler
        })

    def delete_from_waiting(self, chat_id, message_id):
        del self.waiting[f'{chat_id}_{message_id}']

    @manage_waiting_list
    async def process_list_events(
            self,
            bot,
            chat_id: str,
            message_id: str,
            data: Optional[List[Dict]] = None
    ) -> bool:
        if data:
            # generate keyboard with events
            pass
        else:
            # edit message: there are no events
            pass
        # add back button
        return True

    @manage_waiting_list
    async def get_confirmation(
            self,
            bot,
            chat_id: str,
            message_id: str,
            data: Dict[str, str]
    ) -> bool:
        """
        Processing result of an operation that returns just a status:
        success or failure.
        """
        command_name = [key for key in data.keys()][0]
        succeed = data[command_name]
        if succeed:
            # send a message that operation was succeeded
            pass
        else:
            # send a message that operation failed
            pass
        return True
