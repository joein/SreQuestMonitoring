import threading
import json
import subprocess

from telegram.ext import Updater

from config import Config


def ping(ip_addr, addr_map, thread_lock, prev_statuses):
    status = False
    try:
        subprocess.check_call(['ping', '-c', '2', ip_addr], stdout=subprocess.PIPE)
        status = True
    except subprocess.CalledProcessError:
        pass
    finally:
        thread_lock.acquire()
        statuses[ip_addr] = status
        if ip_addr not in previous_statuses or statuses[ip_addr] != prev_statuses[ip_addr]:
            key = "OK" if status else "PROBLEM"
            name = "NOPING"
            bot.sendMessage(chat_id=Config.PRIVATE_CHAT_ID, text=f'{key}: {addr_map[ip_addr]} {name}')
        thread_lock.release()


updater = Updater(Config.TOKEN)
bot = updater.dispatcher.bot


ping_ips = Config.PING_IPS
address_map = Config.ADDRESS_MAP
statuses = {}

lock = threading.Lock()
created_threads = []


with open('ping_status.json', 'r') as json_data:
    previous_statuses = json.load(json_data)

for ip in ping_ips:
    thread = threading.Thread(target=ping, args=(ip, address_map, lock, previous_statuses))
    thread.start()
    created_threads.append(thread)

for thread in created_threads:
    thread.join()

print(statuses)
with open('ping_status.json', 'w') as outfile:
    json.dump(statuses, outfile)
