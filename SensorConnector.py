import os

import serial
import time
import json

import requests
from datetime import datetime as dt
from pytz import timezone

DEBUG = os.environ.get('DEBUG') == '1'
POST_WEB = os.environ.get('POST_WEB') == '1'
POST_TEAMS = os.environ.get('POST_TEAMS') == '1'

POST_INTERVAL = float(os.environ.get('POST_INTERVAL', 5*60))
DOOR_POST_INTERVAL = float(os.environ.get('DOOR_POST_INTERVAL', 5))

SERIAL_PORT = os.environ.get('SERIAL_PORT', '/dev/ttyACM0')
# SERIAL_PORT = 'COM7'
SERIAL_BAUDRATE = int(os.environ.get('SERIAL_BAUDRATE', 38400))

WEB_API_TOKEN_ENDPOINT = os.environ.get('WEB_API_TOKEN_ENDPOINT')
WEB_API_ENDPOINT = os.environ.get('WEB_API_ENDPOINT')
WEB_AUTH_USER = os.environ.get('WEB_AUTH_USER')
WEB_AUTH_PASSWORD = os.environ.get('WEB_AUTH_PASSWORD')
if WEB_API_TOKEN_ENDPOINT is None or WEB_API_ENDPOINT is None:
    print('API URL not provided')
    POST_WEB = False

TEAMS_INCOMING_WEBHOOK_URL = os.environ.get('TEAMS_INCOMING_WEBHOOK_URL')
if TEAMS_INCOMING_WEBHOOK_URL is None:
    print('Teams incoming webhook URL not provided')
    POST_TEAMS = False

TIMEZONE = os.environ.get('TIMEZONE', 'Asia/Tokyo')

COOKIES = None
TOKEN = None

def now_aware():
    return dt.now(timezone(TIMEZONE))

def prepare_token():
    global COOKIES, TOKEN

    print('GET', WEB_API_TOKEN_ENDPOINT)
    r = requests.get(WEB_API_TOKEN_ENDPOINT, auth=( WEB_AUTH_USER, WEB_AUTH_PASSWORD ), cookies=COOKIES)
    res = json.loads(r.text)

    COOKIES = r.cookies
    TOKEN = res['token']

def post2api(data):
    print('POST to API:', WEB_API_ENDPOINT)
    data['token'] = TOKEN
    if not DEBUG:
        requests.post(WEB_API_ENDPOINT, data=data, auth=( WEB_AUTH_USER, WEB_AUTH_PASSWORD ), cookies=COOKIES)
    else:
        print(data)

def post2teams(data):
    print('POST to Teams')
    if not DEBUG:
        requests.post(TEAMS_INCOMING_WEBHOOK_URL, data=json.dumps(data), headers={
            'content-type': 'application/json',
        })
    else:
        print(data)


if __name__ == '__main__':
    prepare_token()

    ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE)
    time.sleep(3) # wait for connecton established

    try:
        print('# start')
        lastPost = 0
        lastDoorPost = 0

        while True:
            line = ser.readline()
            now = time.time()

            #print(line)
            try:
                line = line.decode('ascii').strip()
            except UnicodeDecodeError:
                continue

            try:
                serialData = json.loads(line)
            except json.JSONDecodeError:
                continue

            msgType = serialData.get('type')

            if msgType == 'sensor':
                elapsed = now - lastPost
                if elapsed < POST_INTERVAL:
                    continue

                light = serialData.get('light')
                temperature = serialData.get('temperature')
                if light is None or temperature is None:
                    continue

                print(serialData)

                if POST_WEB:
                    timestamp = now_aware().isoformat()
                    data = {
                        'light': light,
                        'temperature': temperature,
                        'timestamp': timestamp,
                    }
                    post2api(data)

                if POST_TEAMS:
                    # Teams
                    timestamp = now_aware()
                    celsiusTmpr = ((temperature / 1023 * 5.0) - 0.6) / 0.01
                    celsiusTmpr -= 11.3 # hand-fix

                    msg = 'Brightness: %d\n\nTemperature: %.02f ℃\n\nTimestamp: %s' % (light, celsiusTmpr, timestamp.isoformat())
                    data ={
                        'title': 'Sensor Notification',
                        'text': msg,
                    }
                    post2teams(data)

                lastPost = now

            elif msgType == 'doorSensor':
                elapsed = now - lastDoorPost
                if elapsed < DOOR_POST_INTERVAL:
                    continue

                doorState = serialData.get('doorState')
                if doorState is None:
                    continue

                print(serialData)

                if POST_TEAMS:
                    timestamp = now_aware()
                    msg = '%s (Timestamp: %s)' % (doorState, timestamp.isoformat())
                    data ={
                        'title': 'DoorState Notification',
                        'text': msg,
                    }
                    post2teams(data)

                lastDoorPost = now

    except KeyboardInterrupt:
        print('# exit')
        ser.close()
