import os

import time
import json

import requests
from datetime import datetime as dt
from pytz import timezone

from .SensorConnectorConfig import parse_config

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
    config = parse_config()
    # TODO:

    prepare_token()

    ser = SensorSerial(port=SERIAL_PORT, baudrate=baudrate)

    print('# start')
    lastPost = 0
    lastDoorPost = 0

    try:
        for sensor_data in ser.read_json():
            now = time.time()

            msg_type = sensor_data.get('type')

            if msg_type == 'sensor':
                elapsed = now - lastPost
                if elapsed < POST_INTERVAL:
                    continue

                light = sensor_data.get('light')
                temperature = sensor_data.get('temperature')
                if light is None or temperature is None:
                    continue

                print(sensor_data)

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

            elif msg_type == 'doorSensor':
                elapsed = now - lastDoorPost
                if elapsed < DOOR_POST_INTERVAL:
                    continue

                doorState = sensor_data.get('doorState')
                if doorState is None:
                    continue

                print(sensor_data)

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
