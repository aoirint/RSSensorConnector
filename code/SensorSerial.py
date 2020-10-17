import serial

class SensorSerial:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate

    def read_json(self):
        # TODO: reconnect

        ser = serial.Serial(self.port, self.baudrate)
        time.sleep(3) # wait for connecton established

        while True:
            line = ser.readline()

            #print(line)
            try:
                line = line.decode('ascii').strip()
            except UnicodeDecodeError:
                continue

            try:
                sensor_data = json.loads(line)
            except json.JSONDecodeError:
                continue

            yield sensor_data
