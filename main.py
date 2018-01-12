#!/usr/bin/env python3

import re
import sys
from configparser import ConfigParser

from telethon import TelegramClient
from telethon.errors import (InviteHashInvalidError,
                             SessionPasswordNeededError,
                             UsernameNotOccupiedError)
from telethon.tl.entity_database import EntityDatabase
from telethon.tl.functions.channels import (JoinChannelRequest,
                                            ReadHistoryRequest)
from telethon.tl.functions.messages import (CheckChatInviteRequest,
                                            ForwardMessagesRequest,
                                            ImportChatInviteRequest)
from telethon.tl.types import (ChatInvite, ChatInviteAlready, InputPeerSelf,
                               UpdateEditChannelMessage,
                               UpdateNewChannelMessage)

config = ConfigParser()
config.read('config.ini')

api_id = config.getint('common', 'api_id')
api_hash = config.get('common', 'api_hash')
session_name = config.get('common', 'session_name', fallback='default')

if not api_id or not api_hash:
    sys.exit('Exiting, api_id and api_hash cannot be empty.')

client = TelegramClient(session_name, api_id, api_hash,
                        update_workers=1, spawn_read_thread=False)
client.connect()

if not client.is_user_authorized():
    phone = config.get('common', 'phone_number')
    while not phone:
        phone = input('Enter your phone number in international format: ')
    client.send_code_request(phone)
    me = None
    while not me:
        code = None
        while not code:
            code = input('Enter the code you just received: ')
        try:
            me = client.sign_in(code=code)
        except SessionPasswordNeededError:
            password = None
            while not password:
                password = input('Please enter your password: ')
            me = client.sign_in(password=password)

channel_ids = []

for username in config.get('watcher', 'channels').split(','):
    channel, is_private = EntityDatabase.parse_username(username)

    if is_private:
        try:
            invite = client(CheckChatInviteRequest(channel))

            if isinstance(invite, ChatInviteAlready):
                channel_ids.append(invite.chat.id)

            elif isinstance(invite, ChatInvite):
                updates = client(ImportChatInviteRequest(channel))
                channel_ids.append(updates.chats[0].id)

        except InviteHashInvalidError:
            print('The invite link {} is not valid.'.format(
                username.strip()), file=sys.stderr)

    else:
        try:
            channel = client.get_input_entity(channel)
            updates = client(JoinChannelRequest(channel))
            channel_ids.append(channel.channel_id)

        except UsernameNotOccupiedError:
            print('The username {} does not exist.'.format(
                username.strip()), file=sys.stderr)

        except TypeError:
            print('The username {} does not belong to a channel.'.format(
                username.strip()), file=sys.stderr)

if not channel_ids:
    sys.exit('Exiting, there is no channel to watch.')

patterns = [p.strip() for p in config.get('watcher', 'patterns').split(',')]

if not patterns:
    sys.exit('Exiting, there is no pattern to search.')

recipient = config.get('watcher', 'forward_to', fallback='me')
if recipient in ('me', 'self'):
    recipient = InputPeerSelf()
else:
    recipient = client.get_input_entity(recipient)


def callback(update):
    if isinstance(update, (UpdateNewChannelMessage,
                           UpdateEditChannelMessage)):
        print('\nReceived a new channel message')
        msg = update.message

        if msg.to_id.channel_id in channel_ids:
            print('The channel is in the watchlist')

            for pattern in patterns:
                if re.match(pattern, msg.message, re.I | re.S) is not None:
                    print('The message matches the pattern "{}"'.format(
                        pattern))
                    channel = client.get_input_entity(msg.to_id)

                    print('Forwarding the message...')
                    client(ForwardMessagesRequest(
                        from_peer=channel,
                        id=[msg.id],
                        to_peer=recipient
                    ))

                    print('Marking the message as read...')
                    client(ReadHistoryRequest(
                        channel=channel,
                        max_id=msg.id
                    ))

                    break


print('Listening for new messages...')
client.add_update_handler(callback)
client.idle()
client.disconnect()
