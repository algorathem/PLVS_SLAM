from pathlib import Path
from rosbags.highlevel import AnyReader

BAG_PATH = '/home/kc/Downloads/good_run1_converted'

with AnyReader([Path(BAG_PATH)]) as reader:
    for connection, timestamp, rawdata in reader.messages():
        if connection.topic == '/pixhawk/vehicle_status/depth':
            msg = reader.deserialize(rawdata, connection.msgtype)
            # This prints EVERY variable inside the message
            print(f"Fields in message: {dir(msg)}")
            # This prints the actual values
            print(f"Sample Data: {msg}")
            break # We only need to see one