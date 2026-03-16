import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import matplotlib.animation as animation
"""
Research Summary for Step-14
This counter quantifies the Structural Fatigue caused by processing latency.
 In your paper, you can argue that a vessel's lifespan is not limited by fuel, 
 but by the cumulative number of "Hammer Blows" it can withstand before the atomic 
 structure of the hull reaches its decoherence limit.

"""
# --- Simulation Constants ---
GRID_RES = 250
HEIGHT, WIDTH = 10.0, 4.0
TOLERANCE = 0.15  # Max allowable phase deviation before impact

z_vals = np.linspace(0, HEIGHT, GRID_RES)
x_vals = np.linspace(-WIDTH/2, WIDTH/2, GRID_RES // 2)
X, Z = np.meshgrid(x_vals, z_vals)

fig, (ax_metric, ax_locked) = plt.subplots(1, 2, figsize=(14, 9))
plt.subplots_adjust(bottom=0.3)
fig.set_facecolor('#050505')

# Initial Plots
im_m = ax_metric.imshow(np.zeros((GRID_RES, GRID_RES // 2)), cmap='RdGy', 
                        extent=[-WIDTH/2, WIDTH/2, 0, HEIGHT], origin='lower', vmin=-2, vmax=2)
im_l = ax_locked.imshow(np.zeros((GRID_RES, GRID_RES // 2)), cmap='magma', 
                        extent=[-WIDTH/2, WIDTH/2, 0, HEIGHT], origin='lower', vmin=0, vmax=2)

drone_dot, = ax_metric.plot([0], [5.0], 'o', color='lime', markersize=12, label="Vessel")

for ax in [ax_metric, ax_locked]:
    ax.axis('off')
    ax.set_facecolor('#000')

# Text overlays for data tracking
hammer_text = fig.text(0.4, 0.99, "HAMMER BLOWS: 0", color='red', fontsize=14, fontweight='bold')
status_text = fig.text(0.1, 0.99, "STATE: ISENTROPIC GHOST", color='cyan', fontsize=12)

# --- Widgets ---
ax_freq = plt.axes([0.2, 0.18, 0.6, 0.03], facecolor='#222')
ax_lag  = plt.axes([0.2, 0.13, 0.6, 0.03], facecolor='#222')
ax_pos  = plt.axes([0.2, 0.08, 0.6, 0.03], facecolor='#222')
ax_btn  = plt.axes([0.4, 0.02, 0.2, 0.04], facecolor='#333')

s_freq = Slider(ax_freq, 'Vorticity (k)', 0.5, 10.0, valinit=3.0, color='cyan')
s_lag  = Slider(ax_lag,  'Governor Lag ', 0.8, 1.2, valinit=1.0, color='red')
s_pos  = Slider(ax_pos,  'Manual Alt   ', 1.0, 9.0, valinit=5.0, color='lime')
btn_sync = Button(ax_btn, 'Auto-Sync: OFF', color='#444', hovercolor='#555')

# --- State ---
state = {"t": 0, "auto_sync": False, "drone_z": 5.0, "hammer_count": 0, "is_hit": False}

def toggle_sync(event):
    state["auto_sync"] = not state["auto_sync"]
    btn_sync.label.set_text(f"Auto-Sync: {'ON' if state['auto_sync'] else 'OFF'}")
    btn_sync.color = '#006600' if state["auto_sync"] else '#444'

btn_sync.on_clicked(toggle_sync)

def update(i):
    if not plt.fignum_exists(fig.number): return im_m, im_l, drone_dot
    
    state["t"] += 0.1
    k = s_freq.val
    lag = s_lag.val
    
    # 1. Physics Engine
    phi_up = np.sin(k * Z - state["t"])
    phi_down = np.sin(k * (HEIGHT - Z) - (state["t"] * lag))
    phi_total = phi_up + phi_down
    locked_energy = (phi_up**2 + phi_down**2) - (phi_total**2 / 2)
    vortex_focus = np.exp(-X**2 / 0.5)

    # 2. Solver / Governor Logic
    drift_offset = (state["t"] * (lag - 1.0)) / k
    nodes = (np.arange(1, 10) * np.pi / k) + (drift_offset % (np.pi/k))
    
    if state["auto_sync"]:
        idx = np.abs(nodes - state["drone_z"]).argmin()
        target_z = nodes[idx]
        state["drone_z"] += (target_z - state["drone_z"]) * 0.2
    else:
        state["drone_z"] = s_pos.val

    # 3. Hammer Blow Detection Logic
    # Calculate local Metric Tension at drone position
    local_interaction = abs(np.sin(k * state["drone_z"] - state["t"]) + 
                            np.sin(k * (HEIGHT - state["drone_z"]) - (state["t"] * lag)))
    
    if local_interaction > TOLERANCE:
        if not state["is_hit"]: # Edge trigger to prevent runaway counting
            state["hammer_count"] += 1
            state["is_hit"] = True
            fig.patch.set_facecolor('#330000') # Visual flash
        status_text.set_text("STATE: METRIC INTERACTION (HIT!)")
        status_text.set_color('red')
    else:
        state["is_hit"] = False
        fig.patch.set_facecolor('#050505')
        status_text.set_text("STATE: ISENTROPIC GHOST")
        status_text.set_color('cyan')

    hammer_text.set_text(f"HAMMER BLOWS: {state['hammer_count']}")
    
    # 4. Render
    im_m.set_array(phi_total * vortex_focus)
    im_l.set_array(locked_energy * vortex_focus)
    drone_dot.set_data([0], [state["drone_z"]])
    
    return im_m, im_l, drone_dot

ani = animation.FuncAnimation(fig, update, interval=30, blit=True)
plt.show()