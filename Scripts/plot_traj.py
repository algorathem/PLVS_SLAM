import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

file_path = '/home/kc/Desktop/plvs/Scripts/Results/f_dataset_Mecatron_Dataset_mono.txt'

# Load the full trajectory
data = pd.read_csv(file_path, sep=' ', header=None, 
                   names=['ts', 'x', 'y', 'z', 'qx', 'qy', 'qz', 'qw'])

# Detect Resets: A reset occurs if the timestamp jumps significantly 
# or the position snaps back to (0,0)
data['map_id'] = (data['ts'].diff() > 1.0).cumsum() 

plt.figure(figsize=(12, 8))
colors = plt.cm.get_cmap('tab10', 10)

for m_id in data['map_id'].unique():
    subset = data[data['map_id'] == m_id]
    if len(subset) > 5:  # Only plot segments with meaningful data
        plt.plot(subset['x'], subset['y'], label=f'Map ID {m_id}', 
                 color=colors(m_id % 10), linewidth=1.5)

plt.title('Segmented AUV Trajectory (Identifying Individual Map Failures)')
plt.xlabel('X (meters)')
plt.ylabel('Y (meters)')
plt.axis('equal')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()