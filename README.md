# tegracli

![The TEGRACLI logo](https://github.com/Leibniz-HBI/tegracli/blob/trunk/tegracli.png?raw=true)

A convenience wrapper around Telethon and the Telegram Client API for research purposes.

# Installation Instructions

`tegracli` uses Poetry and python >= 3.9 and < 4.0 for building and installing.

To install using pipx, run the following command `pipx install tegracli`.

## How to get API keys

If you don't have API keys for Telegram, head over to [my.telegram.org](https://my.telegram.org).
Click on [API development tools](https://my.telegram.org/apps), fill the form to create yourself an app and pluck the keys into `tegracli.conf.yml`. The session name can be arbitrary.

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

## CONFIGURE

Opens an interactive prompt for configuring API-access. Aks you to input your API id, API hash and session name and requests
a 2FA code from Telegram.

```text
Usage: tegracli configure [OPTIONS]

  Configure tegracli.

Options:
  --help  Show this message and exit.
```

## GET

To _get_ messages from a number of channels, use this command.

```text
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
|---------------------|------------------------------------------------------------------------------------------------------------------------------|
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

```bash
tegracli get --limit 50 corona_infokanal_bmg
```

To retrieve the entire history starting with post #1 of a channel, set `limit` to `-1`.

```bash
tegracli get --reverse --limit -1 corona_infokanal_bmg
```
To retrieve messages sent after January, 1st 2022:

```bash
tegracli get --offset_date 2022-01-01 corona_infokanal_bmg
```

To retrieve message sent before January, 1st 2022:

```bash
tegracli get --reverse --offset_date 2022-01-01 corona_infokanal_bmg
```
## SEARCH

To _search_ messages of your chats and groups and channels you are subscribed to, use this command.

```text
Usage: tegracli search [OPTIONS] [QUERIES]...

  This function searches Telegram content that is available to your account for the specified search term(s).

Options:
  --help  Show this message and exit.
```

## HYDRATE

To rehydrate messages from the API this command accepts a file with message IDs in the format of `$channel_name/$post_number`.
Both input and output file are optional, if not given, `stdin` and `stdout` are used.

Output data is JSONL, one message per line.

```text
Usage: tegracli hydrate [OPTIONS] [INPUT_FILE] [OUTPUT_FILE]

  Hydrate a file with messages-ids.

Options:
  --help  Show this message and exit.
```

For example, to rehydrate message IDs:

```bash
echo test_channel/1234 | tegracli hydrate
>> {"_":"Message","id": 1234, ... , "restriction_reason":[],"ttl_period":null}
```

## GROUP INIT and GROUP RUN

In order to support updatable  and long-running collections `tegracli` sports an *account group* feature which retrieves
the history of a given set of accounts and is able to retrieve updates on each of these accounts.

Groups are initialized by calling `teracli group init`, where accounts to track are stated by either stating them as arguments
or by reading in a file.

### Account Group File Format

Account files are expected to follow these requirements:

- UTF8 text document,
- per line one account, given as either username, channel-URL or ID,
- there shall be no header and  no additional columns

```text
Usage: tegracli group init [OPTIONS] NAME [ACCOUNTS]...

  initialize a new account group

Options:
  -f, --read_file PATH         read an account list from a file, one
                               handle/id/url per line.
  -s, --start_date [%Y-%m-%d]  Start date for the collection. Must be in YYYY-
                               MM-DD format.
  -l, --limit INTEGER          number of posts fo retrieve in one run
  --help                       Show this message and exit.
```

A group is essentially a directory in your tegracli project folder which holdes
a group configuration file, a `profiles.jsonl` file which will collect all user objects returned
by Telegram (these will be recycled to save API requests), as well as the jsonl-files containing the messages.
The messages-files are structured in a way that one file holds the messages of one account and is named by the
account's ID.

An exemplary project could look this:

```text
tegracli-project/
 |- tegracli.conf.yml
 |- mysession.session
 |- my_group/
    |- tegracli_group.conf.yml
    |- profiles.jsonl
    |- 10000001.jsonl
    |- 10000002.jsonl
```
To run the project command your terminal to `tegracli group run my_group` to collect the latest post of the accounts you want to track.

```text
Usage: tegracli group run [OPTIONS] [GROUPS]...

  load a group configuration and run the groups operations
```

## Result File Format

Messages are stored in `jsonl`-files per channel or query. For channels filename is the channel's or user's id, for searches the query.
**BEWARE:** how directories and files are structured is subject to active development and prone to changes in the near future.

# Developer Installation

1. Install [poetry](https://python-poetry.org/docs/#installation),
2. Clone repository and unzip, if necessary,
3. In the directory run `poetry install`,
4. Run `poetry shell` to start the development virtualenv,
5. Run `pytest` to run tests, run `pytest --run_api` to include tests against the Telegram API (**these do require a valid configuration**), coverage report can be found under `tests/coverage`.
