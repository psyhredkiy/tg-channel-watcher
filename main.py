#!/usr/bin/env python3

import logging
import re
import sys
from configparser import ConfigParser, NoOptionError, NoSectionError
from time import sleep

from telethon import TelegramClient, utils
from telethon.errors import InviteHashInvalidError, UsernameNotOccupiedError
from telethon.tl.functions.channels import (JoinChannelRequest,
                                            ReadHistoryRequest)
from telethon.tl.functions.messages import (CheckChatInviteRequest,
                                            ForwardMessagesRequest,
                                            ImportChatInviteRequest)
from telethon.tl.types import (ChatInvite, ChatInviteAlready,
                               MessageMediaDocument, MessageMediaPhoto,
                               UpdateEditChannelMessage,
                               UpdateNewChannelMessage)

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logging.getLogger('telethon').setLevel(level=logging.WARNING)

if len(sys.argv) == 1:
    config_file = 'config.ini'

elif len(sys.argv) == 2:
    config_file = sys.argv[1]

else:
    sys.exit('ERROR: command line arguments are not valid.')

config = ConfigParser()
config.read(config_file)

try:
    api_id = config.getint('telethon', 'api_id')
    api_hash = config.get('telethon', 'api_hash')
    session_name = config.get('telethon', 'session_name', fallback='default')
    phone = config.get('telethon', 'phone_number', fallback=None)

except NoSectionError as e:
    txt = 'ERROR: there is no section "{}" in config file "{}".'
    sys.exit(txt.format(e.section, config_file))

except NoOptionError as e:
    txt = 'ERROR: there is no option "{}" in section "{}" ' \
        + 'of config file "{}".'
    sys.exit(txt.format(e.option, e.section, config_file))

except ValueError:
    sys.exit('ERROR: option "api_id" must have an integer value.')

# TODO: spawn_read_thread=False doesn't work in Telethon v0.16.1.1
# https://github.com/LonamiWebs/Telethon/issues/538
client = TelegramClient(session_name, api_id, api_hash,
                        update_workers=4, spawn_read_thread=True)
client.connect()
client.start(phone)

forward_ids = []
download_ids = []

for channel_ids, section in ((forward_ids, 'forwarder'),
                             (download_ids, 'downloader')):
    for username in config.get(section, 'channels', fallback='').split(','):
        if username:
            channel, is_private = utils.parse_username(username)

            if is_private:
                try:
                    invite = client(CheckChatInviteRequest(channel))

                    if isinstance(invite, ChatInviteAlready):
                        channel_ids.append(invite.chat.id)

                    elif isinstance(invite, ChatInvite):
                        updates = client(ImportChatInviteRequest(channel))
                        channel_ids.append(updates.chats[0].id)

                except InviteHashInvalidError:
                    txt = 'Invite link "{}" is not valid.'
                    logging.warning(txt.format(username.strip()))

            else:
                try:
                    channel = client.get_input_entity(channel)
                    client(JoinChannelRequest(channel))
                    channel_ids.append(channel.channel_id)

                except UsernameNotOccupiedError:
                    txt = 'Username "{}" does not exist.'
                    logging.warning(txt.format(username.strip()))

                except TypeError:
                    txt = 'Username "{}" does not belong to a channel.'
                    logging.warning(txt.format(username.strip()))

if forward_ids:
    patterns = [p.strip() for p in config.get(
        'forwarder', 'patterns', fallback='').split(',')]
    if patterns:
        recipient = config.get('forwarder', 'recipient', fallback='me')
        recipient = client.get_input_entity(recipient)
    else:
        txt = 'There is no pattern specified to search for, ' \
            + 'disabling forwarder.'
        logging.warning(txt)
        forward_ids = None

if download_ids:
    save_photos = config.getboolean(
        'downloader', 'download_photos', fallback=False)
    save_files = config.getboolean(
        'downloader', 'download_files', fallback=False)
    if save_photos or save_files:
        download_directory = config.get(
            'downloader', 'download_directory', fallback='')
        blacklist = [f.strip().lower() for f in config.get(
            'downloader', 'formats_blacklist', fallback='').split(',')]
    else:
        txt = 'Both "download_photos" and "download_files" are false, ' \
            + 'disabling downloader.'
        logging.warning(txt)
        download_ids = None

if not forward_ids and not download_ids:
    txt = 'ERROR: there is no work to do for forwarder, nor for downloader.'
    sys.exit(txt)


def callback(update):
    logging.debug('Received a new update...')
    if isinstance(update, (UpdateNewChannelMessage,
                           UpdateEditChannelMessage)):
        logging.debug('The update is a channel message...')
        msg = update.message

        if msg.to_id.channel_id in forward_ids:
            logging.debug('The channel is in the forwarder list...')
            channel = client.get_input_entity(msg.to_id)

            for pattern in patterns:
                if re.match(pattern, msg.message, re.I | re.S) is not None:
                    txt = 'The message matches the pattern "{}".'
                    logging.debug(txt.format(pattern))

                    logging.debug('Forwarding the message...')
                    client(ForwardMessagesRequest(
                        from_peer=channel,
                        id=[msg.id],
                        to_peer=recipient
                    ))

                    break

            logging.debug('Marking the message as read...')
            client(ReadHistoryRequest(channel=channel, max_id=msg.id))

        if msg.to_id.channel_id in download_ids:
            logging.debug('The channel is in the downloader list...')
            channel = client.get_entity(msg.to_id)
            location = download_directory + \
                (channel.username or str(channel.id)) + '/'

            if isinstance(msg.media, MessageMediaPhoto) and save_photos:
                logging.debug('The message is a photo.')

                logging.debug('Saving the photo...')
                client._download_photo(
                    msg.media,
                    location,
                    msg.date,
                    None
                )

            elif isinstance(msg.media, MessageMediaDocument) and save_files:
                logging.debug('The message is a file...')
                if msg.media.document.mime_type not in blacklist:
                    logging.debug('The file format is not in the blacklist.')

                    logging.debug('Saving the photo...')
                    client._download_document(
                        msg.media,
                        location,
                        msg.date,
                        None
                    )

            logging.debug('Marking the message as read...')
            client(ReadHistoryRequest(channel=channel, max_id=msg.id))


logging.info('Listening for new messages...')
client.add_update_handler(callback)
# TODO: client.idle() doesn't work in Telethon v0.16.1.1
# https://github.com/LonamiWebs/Telethon/issues/538
while True:
    sleep(1)
client.disconnect()
