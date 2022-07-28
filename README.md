# tegracli

A convenience wrapper around Telethon and the Telegram Client API for research purposes.

# Installation Instructions

`tegracli` uses Poetry and python >= 3.9 for building and installing.

To install using pipx, run the following command `pipx install tegracli`.

## How to get API keys

If you don't have API keys for Telegram, head over to [my.telegram.org](https://my.telegram.org). Click on [API development tools](https://my.telegram.org/apps), fill the form to create yourself an app and pluck the keys into `tegracli.conf.yaml`. The session name can be arbitrary.

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

  Get messages for the specified channels by either ID or username.

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
  --reverse / --forward         Should post numbers count upward or downward.
                                Defaults to forward.
  -r, --reply_to TEXT           Only messages replied to specific post id.
  --help                        Show this message and exit.
```
| **parameter**       | **description**                                                                                                              |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **channels**        | a list of of either telegram usernames, channel or group URLs or user IDs.                                                   |
| **limit**           | number of messages to retrieve, positive integer. If set to `-1` , retrieves all messages in the channel. defaults to `-1`.  |
| **offset_date**     | specify start point of retrieval by date, retrieval direction is controlled by `reverse/forward`. Format must be YYYY-MM-DD. |
| **offset_id**       | specify start point of retrieval by post number, retrieval direction is controlled by `reverse/forward`.                     |
| **min_id**          | sets the minimum post number                                                                                                 |
| **max_id**          | sets the maximum post number                                                                                                 |
| **add_offset**      | add a offset to the post numbers to be retrieved                                                                             |
| **from_user**       | limit messages to posts *from* a specific user                                                                               |
| **reply_to**        | limit messages to replies *to* a specific user                                                                               |
| **reverse/forward** | flag to indicate whether messages should be retrieved in chronological or reverse chronological order.                       |

### Basic Examples

To retrieve the last fifty messages from a Telegram channel:

```
tegracli get --limit 50 corona_infokanal_bmg
```

To retrieve the entire history starting with post #1 of a channel, set `limit` to `-1`.

```
tegracli get --reverse --limit -1 corona_infokanal_bmg
```
To retrieve messages sent after Januar, 1st 2022:

```
tegracli get --offset_data 2022-01-01 corona_infokanal_bmg
```

To retrieve message sent before Januar, 1st 2022:

```
tegracli get --reverse --offset_data 2022-01-01 corona_infokanal_bmg
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

Messages are stored in `jsonl`-files per channel or query. For channels filename is the channel's or user's id, for searches the query.
**BEWARE:** how directories and files are layed out is subject to active development and prone to changes in the near future.

# Developer Installation

1. Install [poetry](https://python-poetry.org/docs/#installation),
2. Clone repository and unzip, if necessary,
3. In the directory run `poetry install`,
4. Run `poetry shell` to start the development virtualenv,
6. Run `pytest` to run tests, run `pytest --run_api` too include tests against the Telegram API (**these do require a valid configuration**), coverage report can be found under `tests/coverage`.
