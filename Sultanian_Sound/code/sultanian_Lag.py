import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- Sultanian Parameters ---
GRID_RES = 300
F_PLENUM = 5.2e12       
C_LIGHT = 299792458     
K_SULTANIAN = 2 * np.pi / 0.8 

# --- STRESS TEST PARAMETER ---
# 1.0 = Perfect 5.2 THz Sync
# < 1.0 = Processing Lag (introduces phase drift)
LAG_FACTOR = 1.0

HEIGHT, WIDTH = 10.0, 4.0
z = np.linspace(0, HEIGHT, GRID_RES)
x = np.linspace(-WIDTH/2, WIDTH/2, GRID_RES // 2)
X, Z = np.meshgrid(x, z)

fig, (ax_metric, ax_locked) = plt.subplots(1, 2, figsize=(14, 8))
fig.set_facecolor('#050505')

im_m = ax_metric.imshow(np.zeros((GRID_RES, GRID_RES // 2)), cmap='RdGy', 
                        extent=[-WIDTH/2, WIDTH/2, 0, HEIGHT], origin='lower', vmin=-2, vmax=2)
ax_metric.set_title(r"Metric Potential Interference ($\Phi$)", color='cyan')

im_l = ax_locked.imshow(np.zeros((GRID_RES, GRID_RES // 2)), cmap='magma', 
                        extent=[-WIDTH/2, WIDTH/2, 0, HEIGHT], origin='lower', vmin=0, vmax=2)
ax_locked.set_title(r"Sultanian Locked Energy ($\rho_L$)", color='orange')

drone_dot, = ax_metric.plot([], [], 'o', color='lime', markersize=10, label="Isentropic Ghost")
ax_metric.legend(loc='upper right', facecolor='#111', labelcolor='white')

for ax in [ax_metric, ax_locked]: ax.axis('off')

def update(t):
    # Upbound Metric Pulse
    phi_up = np.sin(K_SULTANIAN * Z - t)
    
    # The Governor attempts to generate the Downbound reflection
    # If LAG_FACTOR < 1.0, the counter-phase drifts away from the node
    phi_down = np.sin(K_SULTANIAN * (HEIGHT - Z) - (t * LAG_FACTOR))
    
    phi_total = phi_up + phi_down
    vortex_focus = np.exp(-X**2 / 0.4)
    locked_energy = (phi_up**2 + phi_down**2) - (phi_total**2 / 2)
    
    im_m.set_array(phi_total * vortex_focus)
    im_l.set_array(locked_energy * vortex_focus)
    
    # Calculate Node position (3rd node)
    # Notice the drone will start to 'wobble' out of the band if lag is present
    node_z = (3 * np.pi / K_SULTANIAN)
    drone_dot.set_data([0], [node_z])
    
    if LAG_FACTOR < 1.0:
        ax_metric.set_title(f"STATUS: DECOHERENCE (LAG={LAG_FACTOR})", color='red')
    
    return im_m, im_l, drone_dot

ani = animation.FuncAnimation(fig, update, interval=30, blit=True)
plt.show()