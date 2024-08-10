"""
Class and setting for main class for managing date-making logic.
"""
from meet_api_controller import GoogleMeetApiController
from message_broker_controller import MessageBrokerController
# also, we probably will need connector to DB, user management, authentication
# these things already exist as separate modules in this repo


class DateMakerService:
    # settings for controllers should be passed using env variables and read
    # inside __init__.py
    meet_api_controller = GoogleMeetApiController()
    message_broker_controller = MessageBrokerController()

    def __init__(self):
        ...

    def run(self):
        ...
