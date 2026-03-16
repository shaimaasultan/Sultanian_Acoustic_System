import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- Standing Wave Parameters ---
GRID_RES = 300
HEIGHT = 10.0
WIDTH = 4.0
F_SOUND = 3.0  # Frequency (Hz)
C_SOUND = 5.0  # Speed (m/s)
K_WAVE = 2 * np.pi * F_SOUND / C_SOUND  # Wave number

# Create Vertical Grid
z = np.linspace(0, HEIGHT, GRID_RES)
x = np.linspace(-WIDTH/2, WIDTH/2, GRID_RES // 2)
X, Z = np.meshgrid(x, z)

fig, (ax_wave, ax_energy) = plt.subplots(1, 2, figsize=(12, 8), gridspec_kw={'width_ratios': [1, 1.2]})
fig.set_facecolor('#050505')

# 1. Vertical Pressure View (Interference)
im_p = ax_wave.imshow(np.zeros((GRID_RES, GRID_RES // 2)), cmap='RdBu', 
                      extent=[-WIDTH/2, WIDTH/2, 0, HEIGHT], origin='lower', vmin=-2, vmax=2)
ax_wave.set_title("Vertical Standing Wave (P)", color='white')

# 2. Vertical Locked Energy View (Nodes)
im_e = ax_energy.imshow(np.zeros((GRID_RES, GRID_RES // 2)), cmap='magma', 
                        extent=[-WIDTH/2, WIDTH/2, 0, HEIGHT], origin='lower', vmin=0, vmax=2)
ax_energy.set_title(r"Vertical Locked Energy ($\rho_L$)", color='white')

for ax in [ax_wave, ax_energy]:
    ax.tick_params(colors='white')
    ax.set_facecolor('#000')

def update(t):
    # A Standing Wave is composed of two traveling waves in opposite directions
    # Wave 1: Upward from Transducer (Bottom)
    # Wave 2: Downward from Reflector (Top)
    wave_up = np.sin(K_WAVE * Z - 2 * np.pi * t)
    wave_down = np.sin(K_WAVE * (HEIGHT - Z) - 2 * np.pi * t)
    
    # Interference Pattern
    pressure = wave_up + wave_down
    
    # Locked Energy Density (The nodes where displacement is zero but potential is high)
    # We add a Gaussian 'beam' to focus the energy in the center like the video
    beam_focus = np.exp(-X**2 / 0.5)
    locked_energy = (wave_up**2 + wave_down**2 - (pressure**2 / 4)) * beam_focus

    im_p.set_array(pressure * beam_focus)
    im_e.set_array(locked_energy)
    
    return im_p, im_e

ani = animation.FuncAnimation(fig, update, interval=30, blit=True)
plt.show()