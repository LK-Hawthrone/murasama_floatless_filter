## MURASAMA VIEW | REAL-TIME SCOPE
# Author: L.K Hawthrone

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import signal_factory as sf

# Configuration
WINDOW_SIZE = 200
t_vec = deque([0]*WINDOW_SIZE, maxlen=WINDOW_SIZE)
raw_vec = deque([0]*WINDOW_SIZE, maxlen=WINDOW_SIZE)
filt_vec = deque([0]*WINDOW_SIZE, maxlen=WINDOW_SIZE)

# Setup Figure
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(16, 9), facecolor='black')
ax.set_facecolor('black')
ax.set_ylim(-3.5, 3.5) # Adjusted for the 1000x scale normalization

line_raw, = ax.plot([], [], color='#FF00FF', alpha=0.4, label='Dirty Signal', linewidth=0.8)
line_filt, = ax.plot([], [], color='#39FF14', label='Murasama Blade', linewidth=2.5)

ax.set_title("MURASAMA SCOPE: REAL-TIME Q15 FILTERING", color='white', loc='left', fontfamily='monospace')
ax.grid(color='#111111', linestyle='--')
ax.legend(loc='upper right', facecolor='black', edgecolor='#333333')

def init():
    line_raw.set_data([], [])
    line_filt.set_data([], [])
    return line_raw, line_filt

def update(frame):
    # 1. Get new data from factory
    t, intent, dirty = sf.get_next_sample()
    filtered = sf.apply_murasama_step(dirty)
    
    # 2. Update deques
    t_vec.append(t)
    raw_vec.append(dirty)
    filt_vec.append(filtered)
    
    # 3. Update lines
    # We use a simple range for X to keep the 'sliding' fixed
    x_axis = list(range(WINDOW_SIZE))
    line_raw.set_data(x_axis, list(raw_vec))
    line_filt.set_data(x_axis, list(filt_vec))
    
    # Dynamically adjust X axis to feel like it's moving
    ax.set_xlim(0, WINDOW_SIZE)
    
    return line_raw, line_filt

# Interval in ms (approx 30Hz)
ani = FuncAnimation(fig, update, frames=None, init_func=init, 
                    blit=True, interval=30, cache_frame_data=False)

plt.tight_layout()
plt.show()