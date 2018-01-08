#!/usr/bin/env python3

import configparser
import re

from telethon import *
from telethon.tl.functions.channels import (JoinChannelRequest,
                                            ReadHistoryRequest)
from telethon.tl.functions.messages import ForwardMessagesRequest
from telethon.tl.types import *

config = configparser.ConfigParser()
config.read('config.ini')
settings = config['settings']

api_id = settings.getint('api_id')
api_hash = settings.get('api_hash')
session_name = settings.get('session_name')
channel_names = [s.strip() for s in settings.get('channel_names').split(',')]
message_filters = [s.strip()
                   for s in settings.get('message_filters').split(',')]
forward_to = settings.get('forward_to')

client = TelegramClient(session_name, api_id, api_hash,
                        update_workers=1, spawn_read_thread=False)
client.connect()

if client.is_user_authorized():
    me = client.get_me()
else:
    user_phone = input('Enter your phone number in international format: ')
    client.send_code_request(user_phone)
    me = client.sign_in(user_phone,
                        input('Enter the code you just received: '))

for channel in channel_names:
    client(JoinChannelRequest(client.get_input_entity(channel)))


def callback(update):
    """Callback method for received Updates"""
    print('I received', update)
    if (isinstance(update, UpdateNewChannelMessage)
            or isinstance(update, UpdateEditChannelMessage)):
        msg = update.message
        channel = client.get_entity(msg.to_id)
        if channel.username.lower() in channel_names:
            for pattern in message_filters:
                if (re.match(pattern, msg.message, re.I | re.S)
                        is not None):
                    client(ForwardMessagesRequest(
                        from_peer=channel,
                        id=[msg.id],
                        to_peer=client.get_input_entity(forward_to)
                    ))
                    client(ReadHistoryRequest(
                        channel=channel,
                        max_id=msg.id
                    ))
                    break


client.add_update_handler(callback)
client.idle()
client.disconnect()
