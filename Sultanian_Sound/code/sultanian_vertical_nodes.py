import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- Sultanian Protocol Parameters ---
GRID_RES = 300
F_PLENUM = 5.2e12       # 5.2 THz Baseline
C_LIGHT = 299792458     # Metric propagation speed
R_MARGIN = 1.1          # Alexander Identity Margin

# Normalized units for simulation visibility
lambda_plenum = C_LIGHT / F_PLENUM
k_sultanian = 2 * np.pi / 0.8 # Scaled for visual clarity on 10m axis

HEIGHT = 10.0
WIDTH = 4.0
z = np.linspace(0, HEIGHT, GRID_RES)
x = np.linspace(-WIDTH/2, WIDTH/2, GRID_RES // 2)
X, Z = np.meshgrid(x, z)

fig, (ax_metric, ax_locked) = plt.subplots(1, 2, figsize=(14, 8))
plt.subplots_adjust(bottom=0.1)
fig.set_facecolor('#050505')

# 1. Metric Potential View (The "Whirlpool" Gradient)
im_m = ax_metric.imshow(np.zeros((GRID_RES, GRID_RES // 2)), cmap='RdGy', 
                        extent=[-WIDTH/2, WIDTH/2, 0, HEIGHT], origin='lower', vmin=-2, vmax=2)
ax_metric.set_title(r"Metric Potential Interference ($\Phi$)", color='cyan')

# 2. Sultanian Locked Energy ($\rho_L$)
im_l = ax_locked.imshow(np.zeros((GRID_RES, GRID_RES // 2)), cmap='magma', 
                        extent=[-WIDTH/2, WIDTH/2, 0, HEIGHT], origin='lower', vmin=0, vmax=2)
ax_locked.set_title(r"Sultanian Locked Energy ($\rho_L$)", color='orange')

for ax in [ax_metric, ax_locked]:
    ax.axis('off')

# Adding a simulated "Particle" (The Ghost Drone) trapped in a node
drone_dot, = ax_metric.plot([], [], 'o', color='lime', markersize=10, label="Isentropic Ghost")
ax_metric.legend(loc='upper right', facecolor='#111', labelcolor='white')

def update(t):
    # Standing wave representing the 'Singularity Column'
    # Upbound Metric Pulse vs Downbound Reflection
    phi_up = np.sin(k_sultanian * Z - t)
    phi_down = np.sin(k_sultanian * (HEIGHT - Z) - t)
    
    # Resultant Potential (The Null Zones are the dark bands)
    phi_total = phi_up + phi_down
    
    # Gaussian concentration toward the center of the Whirlpool
    vortex_focus = np.exp(-X**2 / 0.4)
    
    # Locked Energy Calculation: rho_L = (|phi_up|^2 + |phi_down|^2) - |phi_total|^2
    # This shows where energy is trapped in non-interacting nodes
    locked_energy = (phi_up**2 + phi_down**2) - (phi_total**2 / 2)
    
    im_m.set_array(phi_total * vortex_focus)
    im_l.set_array(locked_energy * vortex_focus)
    
    # Position the Drone in the 3rd Node from the bottom
    node_z = (3 * np.pi / k_sultanian) 
    drone_dot.set_data([0], [node_z])
    
    return im_m, im_l, drone_dot

ani = animation.FuncAnimation(fig, update, frames=np.linspace(0, 20, 200), interval=30, blit=True)
plt.show()