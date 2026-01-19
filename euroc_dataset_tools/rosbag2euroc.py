import os
import cv2
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader

# --- CONFIG ---
BAG_PATH = '/home/kc/Downloads/good_run1_converted'
OUTPUT_DIR = '/home/kc/Downloads/AUV_Mecatron_Dataset/mav0'
# --------------

def run_extraction():
    # Create folders for all sensors
    for d in ['cam0/data', 'imu0', 'state_groundtruth_estimate0', 'depth', 'dvl_vel']:
        os.makedirs(os.path.join(OUTPUT_DIR, d), exist_ok=True)

    with AnyReader([Path(BAG_PATH)]) as reader:
        # Open CSVs (No headers for PLVS compatibility)
        cam_f = open(os.path.join(OUTPUT_DIR, 'cam0/data.csv'), 'w')
        imu_f = open(os.path.join(OUTPUT_DIR, 'imu0/data.csv'), 'w')
        gt_f  = open(os.path.join(OUTPUT_DIR, 'state_groundtruth_estimate0/data.csv'), 'w')
        dep_f = open(os.path.join(OUTPUT_DIR, 'depth/data.csv'), 'w')
        vel_f = open(os.path.join(OUTPUT_DIR, 'dvl_vel/data.csv'), 'w')

        print("🚀 Extracting all sensors (Cam, IMU, DR, Depth, Velocity)...")

        for connection, timestamp, rawdata in reader.messages():
            msg = reader.deserialize(rawdata, connection.msgtype)

            # 1. CAMERA
            if connection.topic == '/yolo_node_1/annotated_frame/compressed':
                img = cv2.imdecode(np.frombuffer(msg.data, np.uint8), cv2.IMREAD_COLOR)
                if img is not None:
                    cv2.imwrite(os.path.join(OUTPUT_DIR, f"cam0/data/{timestamp}.png"), img)
                    cam_f.write(f"{timestamp},{timestamp}.png\n")

            # 2. IMU / POSE
            elif connection.topic == '/pixhawk/vehicle_status/pose':
                q, p = msg.pose.orientation, msg.pose.position
                imu_f.write(f"{timestamp},{q.x},{q.y},{q.z},{q.w},{p.x},{p.y},{p.z}\n")

            # 3. DVL DEAD RECKONING (Position Ground Truth)
            elif connection.topic == '/dvl/dead_reckoning':
                # The data is in a list/array: [X, Y, Z]
                x = msg.position[0]
                y = msg.position[1]
                z = msg.position[2]
                gt_f.write(f"{timestamp},{x},{y},{z}\n")
            # 4. DVL VELOCITY (The missing piece!)
            elif connection.topic == '/dvl/velocity':
                # Attempts to find vx/vy/vz or velocity.x/y/z
                vx = getattr(msg, 'vx', getattr(getattr(msg, 'velocity', None), 'x', 0))
                vy = getattr(msg, 'vy', getattr(getattr(msg, 'velocity', None), 'y', 0))
                vz = getattr(msg, 'vz', getattr(getattr(msg, 'velocity', None), 'z', 0))
                vel_f.write(f"{timestamp},{vx},{vy},{vz}\n")

            # 5. DEPTH
            elif connection.topic == '/pixhawk/vehicle_status/depth':
                dep_f.write(f"{timestamp},{msg.data}\n")

        # Close all files
        for f in [cam_f, imu_f, gt_f, dep_f, vel_f]: f.close()
        print(f"✅ Finished! Dataset saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    run_extraction()