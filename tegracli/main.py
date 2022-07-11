import datetime
import time
from typing import Dict
from pathlib import Path
import ujson
import click
import yaml
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from loguru import logger as log

@click.command()
@click.option('--offset_id', '-o')
@click.argument('users', nargs=-1)
def cli(offset_id, users):
   
    conf_path = Path('tegracli.conf.yml')

    if not conf_path.exists():
        return 128
        
    with conf_path.open('r', encoding='UTF-8') as config:
        conf = yaml.safe_load(config)

    session_name = conf["session_name"]
    api_id   = conf["api_id"]
    api_hash = conf["api_hash"]

    client = TelegramClient(session_name, api_id, api_hash)
    client.flood_sleep_threshold = 15 * 60


    params = {}

    if offset_id is not None:
        params["offset_id"] = int(offset_id)

    with client:
        client.loop.run_until_complete(main(users, client, params=params))

def str_dict(d):
    if type(d) is dict:
        return {k:str_dict(v) for (k,v) in d.items()}
    elif d is None:
        return d
    elif type(d) is list:
        return [str_dict(v) for v in d]
    elif type(d) is datetime.datetime:
        return d.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return str(d)

async def main(users, client: TelegramClient, params: Dict):
    # assert client.connect()
    if not await client.is_user_authorized():
        phone_number = click.prompt('Enter your phone number:')
        await client.send_code_request(phone_number)
        await client.sign_in(phone_number, click.prompt('Enter code: '))
    me = await client.get_me()

    log.info(f'Using telegram account of {me.to_dict().get("username")}')
    
    for user in users:
        try:
            other = await client.get_entity(user)
            o_dict = other.to_dict()

            n = 0
            async for message in client.iter_messages(other, limit=None, reverse=True, wait_time=10, **params):
                log.debug(f'Received: {other.username}-{message.id}')
                with Path(f"{other.id}.jsonl").open('a') as file:
                    m_dict = message.to_dict()
                    m_dict["user"] = o_dict
                    ujson.dump(str_dict(m_dict), file)
                    n += 1
                    file.write('\n')
        except FloodWaitError as err:
            log.error(f'FloodWaitError occurred. Waiting for {datetime.timedelta(seconds=err.seconds)} to resume.')
            time.sleep(err.seconds)
        except Exception as err:
            log.error(f'No dice for {user}, because {err}')
            continue
        log.info(f'Fetched {n} messages for {other.to_dict().get("title")}!')
    await client.send_message('me', f'Hello, myself! I\'m done with {", ".join(users)}!')

async def search(queries, client: TelegramClient):
    me = await client.get_me()
    log.info(f'Using telegram accout of {me.to_dict().get("username")}')
    for query in queries:
        n = 0
        try:
            async for message in client.iter_messages(None, search=query, limit=15):
                with Path(f"{query}.jsonl").open('a') as file:
                    m_dict = message.to_dict()
                    ujson.dump(str_dict(m_dict), file)
                    n += 1
                    file.write('\n')
        except Exception as e:
            log.error(f'No dice for {query}, because {e}')
            continue
        log.info(f'Fetched {n} messages for {query}!')

if __name__ == 'main':
    cli()
