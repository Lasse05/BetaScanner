#!/usr/bin/env python
from bt_proximity import BluetoothRSSI
import datetime
import time
import threading
import sys
import subprocess
import paho.mqtt.client as mqtt
import json
import hashlib

with open('/home/pi/data.json') as json_file:
    data = json.load(json_file)
name = data['id']
ip = data['ip']
BT_ADDR_LIST = []
threads = []
def encrypt_string(hash_string):
    sha_signature = \
        hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature
def statusupdate(status):
    client.publish("status" + name, status)
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("search" + name)
    statusupdate("ready")

def on_message(client, userdata, msg):
    if msg.topic == "search" + name:
        payload = str(msg.payload).split(",")
        addr = payload[0]
        time_sleep = payload[1]
        new_addr = True
        for addr_ in BT_ADDR_LIST:
            if addr_ == addr:
                new_addr = False
        if new_addr:
            BT_ADDR_LIST.append(addr)
            print(addr)
            time.sleep(float(time_sleep))
            th = start_thread(addr=addr, callback=dummy_callback)
            threads.append(th)


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print "Unexpected MQTT disconnection. Will auto-reconnect"
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
# List of bluetooth addresses to scan
DAILY = True  # Set to True to invoke callback only once per day per address
DEBUG = True  # Set to True to print out debug messages
SLEEP = 1


def dummy_callback():
    print("test")


def bluetooth_listen(
        addr, callback, sleep=3, daily=True, debug=False):
    while True:      
        b = BluetoothRSSI(addr=addr)
        rssi = b.get_rssi()
        if rssi != None:
            print(addr + str(rssi))
            client.publish("SmartCoast/Daten/" + name, "{\""+ addr + "\":" + str(rssi) + "}")
        time.sleep(3)
    

def start_thread(addr, callback,  sleep=SLEEP,
        daily=DAILY, debug=DEBUG):
    thread = threading.Thread(
        target=bluetooth_listen,
        args=(),
        kwargs={
            'addr': addr,
            'callback': callback,
            'sleep': sleep,
            'daily': daily,
            'debug': debug
        }
    )
    # Daemonize
    thread.daemon = True
    
    # Start the thread
    thread.start()
    print("Start thread")
    return thread


def main():
    while True:
        time.sleep(1)
client.username_pw_set(name,encrypt_string(name))

client.connect(ip, 1883)

client.loop_forever()

if __name__ == '__main__':
    main()
