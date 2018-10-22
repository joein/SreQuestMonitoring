import subprocess
import json
import time
from copy import deepcopy

from telegram.ext import Updater

from config import Config


ping_ips = Config.PING_IPS
curl_ips = Config.CURL_IPS

updater = Updater(Config.TOKEN)
bot = updater.dispatcher.bot 

def ping(ip_addr):
    current_status = dict(OK=[], ERROR=[])
    try:
        subprocess.check_call(['ping', '-c', '2', ip_addr])
        current_status["OK"].append(ip_addr)
    except subprocess.CalledProcessError:
        current_status["ERROR"].append(ip_addr)
    finally:
        return current_status


def curl(ip_addr):
    current_status = dict(OK=[], ERROR=[])
    try:
        subprocess.check_call(['curl', ip_addr])
        current_status["OK"].append(ip_addr)
    except subprocess.CalledProcessError:
        current_status["ERROR"].append(ip_addr)
    finally:
        return current_status


def get_stopped_tracking_ips(previous_ips, current_ips):
    return list(set(previous_ips).difference(set(current_ips)))


def write(changed_status_ip):
    to_write = []
    for ip in changed_status_ip:
        to_write.append(ip)
    return to_write


def parse_command_json(json_dict, command):
    return json_dict[command]["OK"], json_dict[command]["ERROR"]


def get_current_command_statuses(func, ips):
    cur_statuses = dict(OK=[], ERROR=[])
    for ip in ips:
        status = func(ip)
        if status["OK"]:
            cur_statuses["OK"].append(ip)
        else:
            cur_statuses["ERROR"].append(ip)
    return cur_statuses


with open('status.json', 'r') as json_data:
    previous_statuses = json.load(json_data)
    previous_pings_ips_ok, previous_pings_ips_error = parse_command_json(previous_statuses, "ping")
    previous_curls_ips_ok, previous_curls_ips_error = parse_command_json(previous_statuses, "curl")


_statuses = dict(OK=[], ERROR=[])
left_previous_ping_statuses = deepcopy(_statuses)
left_previous_curl_statuses = deepcopy(_statuses)

left_previous_ping_statuses["OK"] = get_stopped_tracking_ips(previous_pings_ips_ok, ping_ips)
left_previous_ping_statuses["ERROR"] = get_stopped_tracking_ips(previous_pings_ips_error, ping_ips)
left_previous_curl_statuses["OK"] = get_stopped_tracking_ips(previous_curls_ips_ok, curl_ips)
left_previous_curl_statuses["ERROR"] = get_stopped_tracking_ips(previous_curls_ips_error, curl_ips)
to_write_ping_statuses = deepcopy(left_previous_ping_statuses)
to_write_curl_statuses = deepcopy(left_previous_curl_statuses)
to_send_ping_statuses = deepcopy(_statuses)
to_send_curl_statuses = deepcopy(_statuses)

current_ping_statuses = get_current_command_statuses(ping, ping_ips)
current_curl_statuses = get_current_command_statuses(curl, curl_ips)

changed_ping_statuses_to_ok = set(current_ping_statuses["OK"]) - set(previous_pings_ips_ok)
changed_ping_statuses_to_error = set(current_ping_statuses["ERROR"]) - set(previous_pings_ips_error)
changed_curl_statuses_to_ok = set(current_curl_statuses["OK"]) - set(previous_curls_ips_ok)
changed_curl_statuses_to_error = set(current_curl_statuses["ERROR"]) - set(previous_curls_ips_error)

changed_status = dict(ping=dict(OK=changed_ping_statuses_to_ok,
                                ERROR=changed_ping_statuses_to_error),
                      curl=dict(OK=changed_curl_statuses_to_ok,
                                ERROR=changed_curl_statuses_to_error))

for command in changed_status:
    for key in changed_status[command]:
        for ip in sorted(changed_status[command][key]):
            try:
                bot.sendMessage(chat_id=Config.CHAT_ID, text=f'{key}: {ip} {command}')
                time.sleep(1)
            except TimedOut:
                time.sleep(5)
                bot.sendMessage(chat_id=Config.CHAT_ID, text=f'{key}: {ip} {command}')

to_send_ping_statuses["OK"].extend(write(changed_ping_statuses_to_ok))
to_send_ping_statuses["ERROR"].extend(write(changed_ping_statuses_to_error))
to_send_curl_statuses["OK"].extend(write(changed_curl_statuses_to_ok))
to_send_curl_statuses["ERROR"].extend(write(changed_curl_statuses_to_error))

to_write_ping_statuses["OK"].extend(current_ping_statuses["OK"])
to_write_ping_statuses["ERROR"].extend(current_ping_statuses["ERROR"])
to_write_curl_statuses["OK"].extend(current_curl_statuses["OK"])
to_write_curl_statuses["ERROR"].extend(current_curl_statuses["ERROR"])

statuses = dict(ping=to_write_ping_statuses, curl=to_write_curl_statuses)

with open('status.json', 'w') as outfile:
    json.dump(statuses, outfile)

