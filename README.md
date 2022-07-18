# tegracli

A convenience wrapper around Telethon and the Telegram Client API for research purposes.

# Installation Instructions

`tegracli` uses Poetry and python >= 3.9 for building and installing.
To install using pipx, run ``.

## How to get API keys

If you don't have API keys for Telegram, head over to [my.telegram.org](https://my.telegram.org). Follow the instructions and create yourself an app and pluck the keys into `tegracli.conf.yaml`.

```yaml
api_id: 1234567
api_hash : some12321hashthatmustbehere123
session_name: somesessionyo
```

This template file is provided with the repository.

# Usage

`tegracli` is a terminal application to access the Telegram API for research purposes. 
In order to retrieve messages the configuration-file from the section before must be present in the directory you start `tegracli`. 
The following commands are available:

## GET

To _get_ messages from a number of channels, use this command.

```
Usage: tegracli get [OPTIONS] [CHANNELS]...

  Get messages for the specified channels.

Options:
  -l, --limit INTEGER           Number of messages to retrieve.
  -O, --offset_date [%Y-%m-%d]  Offset retrieval to specific date in YYYY-MM-
                                DD format.
  -o, --offset_id INTEGER       Offset retrieval to a specific post number.
  -m, --min_id INTEGER          Minimal post number.
  -M, --max_id INTEGER          Maximal post number
  -a, --add_offset INTEGER      Add an offset to the post numbers to be
                                retrieved.
  -f, --from_user TEXT          Only messages from this user.
  --reverse / --forward         Post numbers counting upward or downward.
                                Defaults to reverse.
  -r, --reply_to TEXT           Only messages replied to specific 
```

## SEARCH

To _search_ messages of your chats and groups and channels you are subscribed to, use this command.

```
Usage: tegracli search [OPTIONS] [QUERIES]...

  This function searches Telegram content that is available to your account for the specified search term(s).

Options:
  --help  Show this message and exit.
```

## Result File Format

Messages are stored in `jsonl`-files on a per channel/query basis.

# Developer Installation

1. Install [poetry](https://python-poetry.org/docs/#installation)
2. Clone repository
3. In the directory run `poetry install`
4. Run `poetry shell` to start development virtualenv
6. Run `pytest` to run all tests
