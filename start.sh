#!/bin/bash
source /home/c7/SreMonitoringBotS28/venv/bin/activate
while true
do
count=1
python3 /home/c7/SreMonitoringBotS28/heartbeat.py
until [ $count -gt 60 ]
do 
nohup python3 /home/c7/SreMonitoringBotS28/bot.py
sleep 30
count=$(( $count + 1 ))
done
done
deactivate
