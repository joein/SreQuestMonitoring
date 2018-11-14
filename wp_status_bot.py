import json
import asyncio
import aiohttp

from telegram.ext import Updater

from config import Config


async def fetch_async(ip_addr, addr_map):
    url = f'http://{ip_addr}'
    status = False
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    status = True
        except aiohttp.client_exceptions.ClientConnectorError:
            try:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        status = True
            except aiohttp.client_exceptions.ClientConnectorError:

                print(f'error {ip_addr}')
            except asyncio.TimeoutError:
                print(f'error {ip_addr}')

        except asyncio.TimeoutError:
            try:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        status = True
            except aiohttp.client_exceptions.ClientConnectorError:

                print(f'error {ip_addr}')
            except asyncio.TimeoutError:
                print(f'error {ip_addr}')

    if ip_addr not in previous_statuses or status != previous_statuses[ip_addr]:
        key = "OK" if status else "PROBLEM"
        name = "WP is down"
        bot.sendMessage(chat_id=Config.PRIVATE_CHAT_ID, text=f'{key}: {addr_map[ip_addr]} {name}')

    return ip_addr, status


async def asynchronous():
    statuses = {}
    futures = [fetch_async(curl_ips[i - 1], address_map) for i in range(1, len(curl_ips) + 1)]
    for i, future in enumerate(asyncio.as_completed(futures)):
        res = await future
        ip = res[0]
        status = res[1]
        statuses[ip] = status
    return statuses

curl_ips = Config.CURL_IPS
address_map = Config.ADDRESS_MAP
updater = Updater(Config.TOKEN)
bot = updater.dispatcher.bot


with open('curl_status.json', 'r') as json_data:
    previous_statuses = json.load(json_data)

ioloop = asyncio.get_event_loop()
statuses = ioloop.run_until_complete(asynchronous())
ioloop.close()

with open('curl_status.json', 'w') as outfile:
    json.dump(statuses, outfile)

