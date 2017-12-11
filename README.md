# tg-channel-watcher

> A simple script that checks all the messages sent in a given list of
Telegram channels/supergroups and forwards (to yourself or to someone else)
the ones matching a specified filter

To set up the virtual environment and clone the repository, run the following
commands:

```shell
virtualenv -p python3 tg-channel-watcher_ve
cd tg-channel-watcher_ve/
source bin/activate
git clone https://github.com/xates/tg-channel-watcher.git
cd tg-channel-watcher/
pip install -r requirements.txt
```
Before running the script, create a `config.ini` file with your configuration
parameters (see file [example.ini](example.ini) for reference)
