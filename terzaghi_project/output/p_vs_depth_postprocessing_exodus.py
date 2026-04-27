import pyvista as pv
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.lines import Line2D
import numpy as np
import vtk
import os
import shutil
import sys
import logging

# Disable pop-ups and terminal error reporting for VTK & Matplotlib fonts
vtk.vtkObject.GlobalWarningDisplayOff()
pv.set_error_output_file('vtk_errors.log')
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

# ==========================================
# 1. SMART LATEX AUTO-DETECTION
# ==========================================
user_home = os.path.expanduser("~")
possible_paths = [
    r"C:\Program Files\MiKTeX\miktex\bin\x64",
    os.path.join(user_home, r"AppData\Local\Programs\MiKTeX\miktex\bin\x64"),
    r"C:\texlive\2024\bin\windows",
    r"C:\texlive\2023\bin\windows",
]

latex_found = False
if shutil.which("pdflatex"):
    print("✅ Success: LaTeX found in system PATH.")
    latex_found = True
else:
    print("🔍 Searching for LaTeX in common locations...")
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found LaTeX at: {path}")
            os.environ["PATH"] += os.pathsep + path
            latex_found = True
            break

# ==========================================
# 2. Modern & Professional Matplotlib Styling
# ==========================================
mpl.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'Computer Modern Roman', 'serif'],
    'mathtext.fontset': 'cm',          
    'axes.linewidth': 1.5,             
    'axes.labelsize': 14,              
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'xtick.direction': 'in',           
    'ytick.direction': 'in',
    'xtick.top': True,                 
    'ytick.right': True,               
    'xtick.major.size': 6,             
    'xtick.major.width': 1.5,          
    'ytick.major.size': 6,
    'ytick.major.width': 1.5,
    'legend.frameon': False,           
    'legend.fontsize': 12
})

if latex_found:
    print("   -> .pgf export ENABLED.")
    mpl.rcParams.update({
        "pgf.texsystem": "pdflatex",
        "font.family": "serif",
        "text.usetex": False,
        "pgf.rcfonts": False,
    })
else:
    print("⚠️ FAILURE: Could not find a local LaTeX installation.")
    print("   -> .pgf export DISABLED. Will save as .pdf (vector) instead.")

def save_smart(filename_base):
    dir_name = os.path.dirname(filename_base)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    
    plt.savefig(f"{filename_base}.png", dpi=300, bbox_inches='tight')
    
    if latex_found:
        try:
            plt.savefig(f"{filename_base}.pgf", bbox_inches='tight')
            print(f"   Saved: {filename_base}.pgf")
        except Exception as e:
            print(f"   Error saving PGF: {e}")
    else:
        plt.savefig(f"{filename_base}.pdf", bbox_inches='tight')
        print(f"   Saved: {filename_base}.pdf (Fallback)")

# ==========================================
# 3. Data Setup & Reader Initialization
# ==========================================
# Adjusted for the new -500 load case
H_drainage = 10.0   # m
u0_load = 500.0     # kPa (Initial excess pore pressure matches the load magnitude)

ls_reader = pv.get_reader('output/large_strain_load_-500.e')
ss_reader = pv.get_reader('output/small_strain_load_-500.e')

times_p = [1, 10, 30, 100, 365]
colors_p = plt.cm.Blues(np.linspace(0.4, 1.0, len(times_p)))

# ==========================================
# 4. FIGURE 1: Pore Pressure vs. Depth
# ==========================================
fig1, ax1 = plt.subplots(figsize=(8, 6))

for t, color in zip(times_p, colors_p):
    ls_reader.set_active_time_value(t)
    ss_reader.set_active_time_value(t)
    
    ls_mesh = ls_reader.read()
    ss_mesh = ss_reader.read()
    
    if isinstance(ls_mesh, pv.MultiBlock): ls_mesh = ls_mesh.combine()
    if isinstance(ss_mesh, pv.MultiBlock): ss_mesh = ss_mesh.combine()
        
    start_point, end_point = [0.0, 0.0, 0.0], [0.0, 10.0, 0.0]
    ls_line = ls_mesh.sample_over_line(start_point, end_point, resolution=200)
    ss_line = ss_mesh.sample_over_line(start_point, end_point, resolution=200)
    
    ls_depth = 10.0 - ls_line.points[:, 1]
    ss_depth = 10.0 - ss_line.points[:, 1]
    
    ls_p = ls_line.point_data['p']
    ss_p = ss_line.point_data['p']
    
    # Large Strain: Solid Line
    ax1.plot(ls_p, ls_depth, linestyle='-', color=color, linewidth=2)
    # Small Strain: Hollow Circles (Downsampled slightly to avoid overcrowding)
    ax1.plot(ss_p[::4], ss_depth[::4], linestyle='--', color=color, linewidth=2)

ax1.set_xlabel(r"Excess Pore Pressure, $\Delta u$ (kPa)")
ax1.set_ylabel(r"Depth, $z$ (m)")
ax1.set_xlim(left=0) 
ax1.set_ylim(0, 10) 
ax1.invert_yaxis()
ax1.margins(x=0)

# Create custom legends outside the plot
model_handles = [
    Line2D([0], [0], color='black', linestyle='-', linewidth=2, label='Large Strain'),
    Line2D([0], [0], color='black', linestyle='--', linewidth=2, label='Small Strain')
]
time_handles = [Line2D([0], [0], color=c, linewidth=2, label=f'$t={t}$d') for t, c in zip(times_p, colors_p)]

legend1 = ax1.legend(handles=model_handles, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)
ax1.add_artist(legend1)
ax1.legend(handles=time_handles, loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=5)

plt.tight_layout()
plt.subplots_adjust(bottom=0.35) 
save_smart('output/plots/large_vs_small_strain_comparison_plot_load_-500')
plt.show()

# ==========================================
# 5. FIGURE 2: Average Degree of Consolidation vs. Time
# ==========================================
time_values = ss_reader.time_values
U_ls_list = []
U_ss_list = []
t_list = []

for t in time_values:
    ls_reader.set_active_time_value(t)
    ss_reader.set_active_time_value(t)
    
    ls_mesh = ls_reader.read()
    ss_mesh = ss_reader.read()
    
    if isinstance(ls_mesh, pv.MultiBlock): ls_mesh = ls_mesh.combine()
    if isinstance(ss_mesh, pv.MultiBlock): ss_mesh = ss_mesh.combine()
    
    start_point, end_point = [0.0, 0.0, 0.0], [0.0, 10.0, 0.0]
    ls_line = ls_mesh.sample_over_line(start_point, end_point, resolution=200)
    ss_line = ss_mesh.sample_over_line(start_point, end_point, resolution=200)
    
    ls_y = ls_line.points[:, 1]
    ls_p = ls_line.point_data['p']
    sort_idx_ls = np.argsort(ls_y)
    
    ss_y = ss_line.points[:, 1]
    ss_p = ss_line.point_data['p']
    sort_idx_ss = np.argsort(ss_y)
    
    area_p_ls = np.abs(np.trapezoid(ls_p[sort_idx_ls], ls_y[sort_idx_ls]))
    area_p_ss = np.abs(np.trapezoid(ss_p[sort_idx_ss], ss_y[sort_idx_ss]))
    
    initial_area_p = u0_load * H_drainage
    
    # 1. Calculates the fraction correctly here (0.0 to 1.0)
    U_ls = 1.0 - (area_p_ls / initial_area_p)
    U_ss = 1.0 - (area_p_ss / initial_area_p)
    
    U_ls_list.append(U_ls)
    U_ss_list.append(U_ss)
    t_list.append(t)

# Filter out t=0 for logarithmic plotting safely
valid_t = np.array(t_list) > 0
t_log = np.array(t_list)[valid_t]

# 2. FIX: Just multiply the existing fraction by 100. Removed the extra "1 -"
U_ls_log = np.array(U_ls_list)[valid_t] * 100.0
U_ss_log = np.array(U_ss_list)[valid_t] * 100.0

fig2, ax2 = plt.subplots(figsize=(8, 6))

# Large Strain: Solid Line
ax2.plot(t_log, U_ls_log, linestyle='-', color=plt.cm.Blues(0.9), linewidth=2, label=r'MOOSE: Large Strain')

# Small Strain: Dashed Line
ax2.plot(t_log, U_ss_log, linestyle='--', linewidth=2, color=plt.cm.Blues(0.6), label=r'MOOSE: Small Strain')

ax2.set_xlabel(r"Time, $t$ (days)")
ax2.set_ylabel(r"Average Degree of Consolidation, $U$ (%)")
ax2.set_xlim(left=min(t_log), right=max(time_values))

# 3. FIX: Adjust y-limits to frame the percentages properly
ax2.set_ylim(0, 20) 

# Logarithmic X-Axis for transient consolidation
ax2.set_xscale('log')
ax2.margins(x=0)

# Custom legend placed outside at the bottom
ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)

plt.tight_layout()
plt.subplots_adjust(bottom=0.25)
save_smart('output/plots/degree_of_consolidation_comparison_load_-500')
plt.show()