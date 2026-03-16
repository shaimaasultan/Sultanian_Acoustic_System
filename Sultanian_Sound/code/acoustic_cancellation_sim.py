import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- Acoustic Parameters ---
GRID_RES = 250
L = 10.0  
f_sound = 2.0  
c_sound = 5.0  
k_val = 2 * np.pi * f_sound / c_sound  

x = np.linspace(0, L, GRID_RES)
y = np.linspace(0, L, GRID_RES)
X, Y = np.meshgrid(x, y)

S1_pos = np.array([2.0, 5.0])
S2_pos = np.array([8.0, 5.0])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
fig.set_facecolor('#111')

im_p = ax1.imshow(np.zeros((GRID_RES, GRID_RES)), cmap='RdBu', extent=[0, L, 0, L], vmin=-2, vmax=2)
# FIX APPLIED HERE:
ax1.set_title("Acoustic Pressure Interference (P)", color='white')

im_e = ax2.imshow(np.zeros((GRID_RES, GRID_RES)), cmap='inferno', extent=[0, L, 0, L], vmin=0, vmax=2)
# FIX APPLIED HERE:
ax2.set_title(r"Acoustic Energy Density ($\rho_E$)", color='white')

for ax in [ax1, ax2]:
    ax.axis('off')

def update(t):
    r1 = np.sqrt((X - S1_pos[0])**2 + (Y - S1_pos[1])**2)
    r2 = np.sqrt((X - S2_pos[0])**2 + (Y - S2_pos[1])**2)
    
    # Pressure Waves
    p1 = (1/np.sqrt(r1 + 0.5)) * np.sin(k_val * r1 - 2 * np.pi * t)
    p2 = (1/np.sqrt(r2 + 0.5)) * np.sin(k_val * r2 - 2 * np.pi * t + np.pi)
    
    p_total = p1 + p2
    
    # Energy Density (Locked Energy centers)
    energy_density = (p1**2 + p2**2) 
    
    im_p.set_array(p_total)
    im_e.set_array(energy_density)
    return im_p, im_e

ani = animation.FuncAnimation(fig, update, frames=np.linspace(0, 10, 100), interval=50, blit=True)
plt.show()