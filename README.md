# tg-channel-watcher
[![telethon version](https://img.shields.io/badge/telethon-v0.16.1.1-blue.svg)](https://github.com/LonamiWebs/Telethon)
[![license](https://img.shields.io/github/license/xates/tg-channel-watcher.svg)](LICENSE)
[![last commit](https://img.shields.io/github/last-commit/google/skia.svg)](https://github.com/xates/tg-channel-watcher/commits/master)

## Introduction

This project is the combination of two Python3 scripts that I originally
wrote for myself and then I decided to make public so that everyone could
use and improve them. Any contribution is welcome, however please _try_ to
follow the [PEP8 Specification](https://pep8.org) to keep the code clean,
tidy and consistent.

The two components of **tg-channel-watcher** are:

- **forwarder**: checks all the messages sent in a given list of Telegram
channels and forwards (to yourself or to someone else) the ones matching a
specified set of patterns,

- **downloader**: downloads all the media (images and/or documents) sent in
a given list of Telegram channels.

## Getting started

After you have cloned the repository, run the command
`pip install -r requirements.txt` to install all the required dependencies.
You may want to use a [virtual environment](http://bit.ly/1fhx5mq) for
that.

Before running the script, create a configuration file with your settings
(see file [`example.ini`](example.ini) for reference), then, run the script
with the config file as parameter, like that `./main.py config.ini`, or
without any parameter to use the file `config.ini` in the same directory.
