import os
import configargparse as argparse

def parse_config():
    parser = argparse.ArgParser()

    parser.add('--debug', env_var='DEBUG', action='store_true')
    parser.add('--outgoing', env_var='OUTGOING_ENABLED', action='store_true')

    parser.add('--serial-port', env_var='SERIAL_PORT', type=str, default='/dev/ttyACM0')
    parser.add('--serial-baudrate', env_var='SERIAL_BAUDRATE', type=int, default=38400)

    parser.add('--sensor-read-interval', env_var='SENSOR_READ_INTERVAL', type=float, default=5*60)
    parser.add('--door-read-interval', env_var='DOOR_READ_INTERVAL', type=float, default=5)

    parser.add('--timezone', env_var='TIMEZONE', default='Asia/Tokyo')

    config = parser.parse_args()

    if config.outgoing:
        parser = ArgParser.ArgParser(parents=[ parser, ])

        parser.add('--outgoing-api-endpoint', env_var='OUTGOING_API_ENDPOINT', type=str, required=True)
        parser.add('--outgoing-api-key', env_var='OUTGOING_API_KEY', type=str)

        config = parser.parse_args()

    return config
