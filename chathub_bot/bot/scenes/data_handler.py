from collections.abc import Callable
from typing import Dict, List, Optional

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

    async def process_list_events(
            self,
            bot,
            chat_id: str,
            message_id: str,
            data: Optional[List[Dict]] = None
    ):
        try:
            if data:
                # generate keyboard with events
                pass
            else:
                # edit message: there are no events
                pass
            # add back button
            self.delete_from_waiting(chat_id, message_id)
        except:
            # post error into log
            pass
