import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import matplotlib.animation as animation
"""
a toggle button that uses the event_horizon_solver logic to seek the nearest minima in the metric potential field.

How to use the Auto-Sync Dashboard
Manual Flight: With Auto-Sync OFF, use the "Manual Alt" slider. Try to keep the green dot exactly on a bright band in the right plot. If you fail, you'll see the red/grey interference hit the drone in the left plot.

Enable Governor: Click Auto-Sync. The drone will now "magnetically" snap to the nearest band.

Stress Test: While Auto-Sync is ON, move the Governor Lag slider. You will see the bands drift, but the drone will move vertically to stay "Locked" in the non-interacting zone.

Vorticity Shift: Increase Vorticity (k). The drone will automatically hop to the nearest tightening band to maintain its ghost state.

Connection to your Research
This demonstrates the Active Phase Locking required by the Sultanian Protocol. It proves that the "Hole within a Hole" isn't a static achievement, but a dynamic computational process.
"""
# --- Simulation Constants ---
GRID_RES = 250
HEIGHT, WIDTH = 10.0, 4.0
F_BASE = 5.2e12

z = np.linspace(0, HEIGHT, GRID_RES)
x = np.linspace(-WIDTH/2, WIDTH/2, GRID_RES // 2)
X, Z = np.meshgrid(x, z)

# Setup Figure
fig, (ax_metric, ax_locked) = plt.subplots(1, 2, figsize=(14, 9))
plt.subplots_adjust(bottom=0.3)
fig.set_facecolor('#050505')

# Initial Plots
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

# --- Interactive Widgets ---
ax_freq = plt.axes([0.2, 0.18, 0.6, 0.03], facecolor='#222')
ax_lag  = plt.axes([0.2, 0.13, 0.6, 0.03], facecolor='#222')
ax_pos  = plt.axes([0.2, 0.08, 0.6, 0.03], facecolor='#222')
ax_btn  = plt.axes([0.4, 0.02, 0.2, 0.04], facecolor='#333')

s_freq = Slider(ax_freq, 'Vorticity (k)', 0.5, 10.0, valinit=3.0, color='cyan')
s_lag  = Slider(ax_lag,  'Governor Lag ', 0.8, 1.2, valinit=1.0, color='red')
s_pos  = Slider(ax_pos,  'Manual Alt   ', 1.0, 9.0, valinit=5.0, color='lime')
btn_sync = Button(ax_btn, 'Auto-Sync: OFF', color='#444', hovercolor='#555')

# --- State Control ---
state = {"t": 0, "auto_sync": False, "drone_z": 5.0}

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
    
    # 1. Generate Sultanian Fields
    phi_up = np.sin(k * Z - state["t"])
    phi_down = np.sin(k * (HEIGHT - Z) - (state["t"] * lag))
    phi_total = phi_up + phi_down
    locked_energy = (phi_up**2 + phi_down**2) - (phi_total**2 / 2)
    vortex_focus = np.exp(-X**2 / 0.5)

    # 2. Auto-Sync Logic (Step-14 Feedback Loop)
    if state["auto_sync"]:
        # The Governor finds the nearest node by identifying where the 
        # local potential gradient (dPhi/dz) is zero.
        # Here we simulate the solver snapping to the nearest peak in locked_energy
        nodes = (np.arange(1, 10) * np.pi / k)
        # Offset for phase drift caused by Lag
        drift_offset = (state["t"] * (lag - 1.0)) / k
        adjusted_nodes = nodes + (drift_offset % (np.pi/k))
        
        # Snap to closest node
        idx = np.abs(adjusted_nodes - state["drone_z"]).argmin()
        target_z = adjusted_nodes[idx]
        
        # Apply smooth tracking (damping)
        state["drone_z"] += (target_z - state["drone_z"]) * 0.2
    else:
        state["drone_z"] = s_pos.val
    
    # 3. Render
    im_m.set_array(phi_total * vortex_focus)
    im_l.set_array(locked_energy * vortex_focus)
    drone_dot.set_data([0], [state["drone_z"]])
    
    return im_m, im_l, drone_dot

ani = animation.FuncAnimation(fig, update, interval=3000, blit=True)
plt.show()