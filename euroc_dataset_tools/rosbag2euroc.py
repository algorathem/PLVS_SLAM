import os
import cv2
import numpy as np
import yaml
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore

# --- CONFIG ---
BAG_PATH = '/home/kc/Downloads/bag_with_imu_stereo'
OUTPUT_DIR = '/home/kc/Downloads/Kevin_dataset/mav0'
# --------------

def save_camera_yaml(msg, cam_name):
    """Generates the sensor.yaml file required for PLVS/EuRoC format."""
    # Intrinsics: [fu, fv, cu, cv]
    intrinsics = [float(msg.k[0]), float(msg.k[4]), float(msg.k[2]), float(msg.k[5])]
    
    data = {
        'sensor_type': 'camera',
        'comment': f'Kevin {cam_name} camera',
        'resolution': [int(msg.width), int(msg.height)],
        'intrinsics': intrinsics,
        'distortion_model': msg.distortion_model,
        'distortion_coefficients': [float(d) for d in msg.d]
    }
    
    with open(os.path.join(OUTPUT_DIR, cam_name, 'sensor.yaml'), 'w') as f:
        yaml.dump(data, f, default_flow_style=False)

def run_extraction():
    # Create required directory structure
    for d in ['cam0/data', 'cam1/data', 'imu0', 'dvl_vel']:
        os.makedirs(os.path.join(OUTPUT_DIR, d), exist_ok=True)

    # NEW API: Get the latest typestore
    typestore = get_typestore(Stores.LATEST)

    with AnyReader([Path(BAG_PATH)], default_typestore=typestore) as reader:
        cam0_f = open(os.path.join(OUTPUT_DIR, 'cam0/data.csv'), 'w')
        cam1_f = open(os.path.join(OUTPUT_DIR, 'cam1/data.csv'), 'w')
        imu_f  = open(os.path.join(OUTPUT_DIR, 'imu0/data.csv'), 'w')
        vel_f  = open(os.path.join(OUTPUT_DIR, 'dvl_vel/data.csv'), 'w')

        print(f"🚀 Extracting Kevin's Sensors from {BAG_PATH}...")
        
        info_done = {'left': False, 'right': False}

        for connection, timestamp, rawdata in reader.messages():
            msg = reader.deserialize(rawdata, connection.msgtype)

            # 1. Left Camera
            if connection.topic == '/kevin/stereo_camera/left/rgb/compressed':
                img = cv2.imdecode(np.frombuffer(msg.data, np.uint8), cv2.IMREAD_COLOR)
                if img is not None:
                    fname = f"{timestamp}.png"
                    cv2.imwrite(os.path.join(OUTPUT_DIR, f"cam0/data/{fname}"), img)
                    cam0_f.write(f"{timestamp},{fname}\n")

            # 2. Right Camera
            elif connection.topic == '/kevin/stereo_camera/right/rgb/compressed':
                img = cv2.imdecode(np.frombuffer(msg.data, np.uint8), cv2.IMREAD_COLOR)
                if img is not None:
                    fname = f"{timestamp}.png"
                    cv2.imwrite(os.path.join(OUTPUT_DIR, f"cam1/data/{fname}"), img)
                    cam1_f.write(f"{timestamp},{fname}\n")

            # 3. IMU
            elif connection.topic == '/kevin/mavros/imu/data':
                w, a = msg.angular_velocity, msg.linear_acceleration
                imu_f.write(f"{timestamp},{w.x},{w.y},{w.z},{a.x},{a.y},{a.z}\n")

            # 4. DVL Velocity
            elif connection.topic == '/kevin/dvl/data':
                v = msg.twist.twist.linear
                vel_f.write(f"{timestamp},{v.x},{v.y},{v.z}\n")

            # 5. Camera Info
            elif connection.topic == '/kevin/stereo_camera/left/camera_info' and not info_done['left']:
                save_camera_yaml(msg, 'cam0')
                info_done['left'] = True
            elif connection.topic == '/kevin/stereo_camera/right/camera_info' and not info_done['right']:
                save_camera_yaml(msg, 'cam1')
                info_done['right'] = True

        for f in [cam0_f, cam1_f, imu_f, vel_f]: f.close()
        print(f"✅ Extraction complete! Files in {OUTPUT_DIR}")

if __name__ == "__main__":
    run_extraction()