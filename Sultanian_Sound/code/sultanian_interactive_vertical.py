import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import matplotlib.animation as animation
"""
Stress-Testing the Parameters
Vorticity (k): Adjusting this changes the density of the "Cancellation Bands." In a real Black Hole, $k$ increases as you get closer to the center. Note how the bands get thinner and more frequent.
Governor Lag: Move this away from 1.0. You will see the orange bands in the right plot start to slide past the drone. This represents the Governor failing to sync with the plenum, causing the vessel to "pop" out of the null zone.
Drone Alt: Use this to manually navigate the vessel between nodes. In the Sultanian Protocol, you want to keep the green dot centered on a bright orange band in the Locked Energy plot.

Connection to the "Hammer Blow"
If you set the Lag to 0.9 and observe the Metric Potential (Left plot), 
you’ll see the drone is suddenly hit by the red/grey ripples. 
That is the Hammer Blow—the physical impact of the vacuum plenum when the processing speed fails.
"""
# --- Initial Constants ---
GRID_RES = 250
HEIGHT, WIDTH = 10.0, 4.0
F_BASE = 5.2e12  # Reference 5.2 THz

# Setup Grid
z = np.linspace(0, HEIGHT, GRID_RES)
x = np.linspace(-WIDTH/2, WIDTH/2, GRID_RES // 2)
X, Z = np.meshgrid(x, z)

# Setup Figure
fig, (ax_metric, ax_locked) = plt.subplots(1, 2, figsize=(14, 9))
plt.subplots_adjust(bottom=0.25) # Space for sliders
fig.set_facecolor('#050505')

# Initial Plotting
im_m = ax_metric.imshow(np.zeros((GRID_RES, GRID_RES // 2)), cmap='RdGy', 
                        extent=[-WIDTH/2, WIDTH/2, 0, HEIGHT], origin='lower', vmin=-2, vmax=2)
ax_metric.set_title(r"Metric Potential Interference ($\Phi$)", color='cyan')

im_l = ax_locked.imshow(np.zeros((GRID_RES, GRID_RES // 2)), cmap='magma', 
                        extent=[-WIDTH/2, WIDTH/2, 0, HEIGHT], origin='lower', vmin=0, vmax=2)
ax_locked.set_title(r"Sultanian Locked Energy ($\rho_L$)", color='orange')

drone_dot, = ax_metric.plot([0], [5.0], 'o', color='lime', markersize=12, label="Isentropic Ghost")

for ax in [ax_metric, ax_locked]:
    ax.axis('off')
    ax.set_facecolor('#000')

# --- Interactive Sliders ---
ax_color = '#222'
ax_freq = plt.axes([0.2, 0.12, 0.6, 0.03], facecolor=ax_color)
ax_lag  = plt.axes([0.2, 0.07, 0.6, 0.03], facecolor=ax_color)
ax_pos  = plt.axes([0.2, 0.02, 0.6, 0.03], facecolor=ax_color)

s_freq = Slider(ax_freq, 'Vorticity (k)', 0.5, 10.0, valinit=3.0, color='cyan')
s_lag  = Slider(ax_lag,  'Governor Lag ', 0.8, 1.2, valinit=1.0, color='red')
s_pos  = Slider(ax_pos,  'Drone Alt    ', 1.0, 9.0, valinit=5.0, color='lime')

state = {"t": 0}

def update(i):
    if not plt.fignum_exists(fig.number): return im_m, im_l, drone_dot
    
    state["t"] += 0.1
    k = s_freq.val
    lag = s_lag.val
    alt = s_pos.val
    
    # 1. Calculate Sultanian Waves
    phi_up = np.sin(k * Z - state["t"])
    # Downbound wave affected by Lag (Decoherence)
    phi_down = np.sin(k * (HEIGHT - Z) - (state["t"] * lag))
    
    # 2. Potential and Energy Math
    phi_total = phi_up + phi_down
    vortex_focus = np.exp(-X**2 / 0.5)
    
    # Locked energy is where net displacement vanishes but intensity remains
    locked_energy = (phi_up**2 + phi_down**2) - (phi_total**2 / 2)
    
    # 3. Update Visuals
    im_m.set_array(phi_total * vortex_focus)
    im_l.set_array(locked_energy * vortex_focus)
    drone_dot.set_data([0], [alt])
    
    # 4. Status Indicator
    if abs(lag - 1.0) > 0.02:
        ax_metric.set_title("STATUS: TIDAL DECOHERENCE", color='red')
    else:
        ax_metric.set_title(r"Metric Potential Interference ($\Phi$)", color='cyan')
        
    return im_m, im_l, drone_dot

ani = animation.FuncAnimation(fig, update, interval=30, blit=True)
plt.show()