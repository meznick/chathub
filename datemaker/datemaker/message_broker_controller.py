"""
Class and settings for reading/writing messages from queue + logging + additional
things.
"""


class MessageBrokerController:
    def __init__(self):
        ...

    def connect(self):
        ...

    def read(self):
        ...

    def write(self, message):
        ...
