# tg-channel-watcher
[![telethon version](https://img.shields.io/badge/telethon-v0.16.1.1-blue.svg)](https://github.com/LonamiWebs/Telethon)
[![license](https://img.shields.io/github/license/xates/tg-channel-watcher.svg)](LICENSE)
[![last commit](https://img.shields.io/github/last-commit/google/skia.svg)](https://github.com/xates/tg-channel-watcher/commits/master)

## Introduction

This project is the combination of two simple Python 3 scripts that I
originally wrote for myself, and then I decided to make public so that everyone
could make use of and improve them.

Any contribution to the project is highly appreciated and welcome, however,
please _try to_ follow the [PEP8](https://pep8.org) specification in order to
keep the code clean, tidy and consistent.

The two components of **tg-channel-watcher** (which are also the two original
separate projects) are:

- **forwarder**: checks all the messages sent in a list of channels and
forwards (to yourself or to someone else) the ones matching a set of regexes,

- **downloader**: downloads all the media (images and/or documents) sent in a
list of channels, except for the formats specified in a blacklist.

## Getting started

After you have cloned the repository, run the command `pip3 install -r
requirements.txt` to install all the required dependencies.
You may want to use a [virtual environment](http://bit.ly/1fhx5mq) for that.

Before running the script, create a configuration file with your settings using
the file [`example.ini`](example.ini) as reference.
Then, run the script with the configuration file as first parameter, like that
`./main.py config.ini`, or without any parameter to use the `config.ini` file
in the same directory.
