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
    'mathtext.fontset': 'cm',          # Computer Modern for math (LaTeX look)
    'axes.linewidth': 1.5,             # Thicker bounding box
    'axes.labelsize': 14,              # Larger axis labels
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'xtick.direction': 'in',           # Ticks point inwards
    'ytick.direction': 'in',
    'xtick.top': True,                 # Ticks on top axis
    'ytick.right': True,               # Ticks on right axis
    'xtick.major.size': 6,             # Longer major ticks
    'xtick.major.width': 1.5,          # Thicker major ticks
    'ytick.major.size': 6,
    'ytick.major.width': 1.5,
    'legend.frameon': False,           # Remove legend border
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
# 3. Analytical Solution Functions
# ==========================================
def terzaghi_analytical(z_array, t, u0, H, Cv, num_terms=100):
    if t == 0:
        return np.full_like(z_array, u0)
    
    Tv = (Cv * t) / (H ** 2)
    u = np.zeros_like(z_array)
    
    for m in range(num_terms):
        M = (np.pi / 2.0) * (2 * m + 1)
        term = (2.0 * u0 / M) * np.sin(M * z_array / H) * np.exp(- (M ** 2) * Tv)
        u += term
        
    return u

def terzaghi_degree_of_consolidation(t_array, Cv, H, num_terms=100):
    U = np.zeros_like(t_array)
    for i, t in enumerate(t_array):
        if t == 0:
            U[i] = 0.0
            continue
        Tv = (Cv * t) / (H ** 2)
        sum_terms = 0.0
        for m in range(num_terms):
            M = (np.pi / 2.0) * (2 * m + 1)
            sum_terms += (2.0 / (M ** 2)) * np.exp(- (M ** 2) * Tv)
        U[i] = 1.0 - sum_terms
    return U

# --- Material Parameters mapped from MOOSE ---
mu_moose = 2000.0
lambda_moose = 0.0
m_v_moose = 1e-7
kappa_mu_moose = 1e-6

M_constrained = lambda_moose + 2.0 * mu_moose 
S_storage = (1.0 / M_constrained) + m_v_moose
Cv_calc = kappa_mu_moose / S_storage  # ~0.003998 m^2/day

H_drainage = 10.0   # m
u0_load = 1.0    # kPa

# Initialize PyVista Exodus readers
ls_reader = pv.get_reader('output/large_strain_load_-1.e')
ss_reader = pv.get_reader('output/small_strain_load_-1.e')

# ==========================================
# 4. FIGURE 1: Pore Pressure vs. Depth
# ==========================================
times_p = [1, 10, 30, 100, 365]
# Using the theme's blue colormap mapping
colors_p = plt.cm.Blues(np.linspace(0.4, 1.0, len(times_p)))

fig1, ax1 = plt.subplots(figsize=(8, 6))
ana_depth = np.linspace(0, 10.0, 100)

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
    ana_p = terzaghi_analytical(ana_depth, t, u0=u0_load, H=H_drainage, Cv=Cv_calc)
    
    # Large Strain: Solid Line
    ax1.plot(ls_p, ls_depth, linestyle='-', color=color, linewidth=2)
    # Small Strain: Dashed Line
    ax1.plot(ss_p, ss_depth, linestyle=None, color=color, linewidth=2, marker='x', markersize=6, markeredgewidth=1)
    # Analytical: Thick Hollow Circles (sampling fewer points to prevent overlap)
    ax1.plot(ana_p[::5], ana_depth[::5], linestyle='None', marker='o', 
             markerfacecolor='none', markeredgecolor=color, markersize=7, markeredgewidth=2)

ax1.set_xlabel(r"Excess Pore Pressure, $\Delta u$ (kPa)")
ax1.set_ylabel(r"Depth, $z$ (m)")
ax1.set_xlim(left=0) 
ax1.set_ylim(0, 10) 
ax1.invert_yaxis()
ax1.margins(x=0)

# Create custom legends outside the plot
model_handles = [
    Line2D([0], [0], color='black', linestyle='-', linewidth=2, label='Large Strain'),
    Line2D([0], [0], color='black', linestyle='--', linewidth=2, marker='x', markerfacecolor='none', markeredgewidth=2, label='Small Strain'),
    Line2D([0], [0], color='black', linestyle='None', marker='o', markerfacecolor='none', markeredgewidth=2, label='Analytical')
]
time_handles = [Line2D([0], [0], color=c, linewidth=2, label=f'$t={t}$d') for t, c in zip(times_p, colors_p)]

legend1 = ax1.legend(handles=model_handles, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
ax1.add_artist(legend1)
ax1.legend(handles=time_handles, loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=5)

plt.tight_layout()
plt.subplots_adjust(bottom=0.35) 
save_smart('output/plots/analytical_strain_comparison_plot_load_-1')
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
    
    U_ls = 1.0 - (area_p_ls / initial_area_p)
    U_ss = 1.0 - (area_p_ss / initial_area_p)
    
    U_ls_list.append(U_ls)
    U_ss_list.append(U_ss)
    t_list.append(t)

# Analytical U calculation
t_array_ana = np.linspace(0, max(time_values), 200)
U_ana_array = terzaghi_degree_of_consolidation(t_array_ana, Cv_calc, H_drainage)

# Filter out t=0 for logarithmic plotting
valid_t = np.array(t_list) > 0
t_log = np.array(t_list)[valid_t]
U_ls_log = np.array(U_ls_list)[valid_t] * 100
U_ss_log = np.array(U_ss_list)[valid_t] * 100

valid_ana = t_array_ana > 0
t_ana_log = t_array_ana[valid_ana]
U_ana_log = U_ana_array[valid_ana] * 100

fig2, ax2 = plt.subplots(figsize=(8, 6))

# Large Strain: Solid Line
ax2.plot(t_log, U_ls_log, linestyle='-', color=plt.cm.Blues(0.8), linewidth=2, label=r'MOOSE: Large Strain')
# Small Strain: Dashed Line
ax2.plot(t_log, U_ss_log, linestyle='--', color=plt.cm.Blues(0.5), linewidth=2.5, label=r'MOOSE: Small Strain')
# Analytical: Thick Hollow Circles
ax2.plot(t_ana_log[::5], U_ana_log[::5], linestyle='None', marker='o', 
         markerfacecolor='none', markeredgecolor='black', markersize=6, markeredgewidth=2, label=r'Terzaghi Analytical')

ax2.set_xlabel(r"Time, $t$ (days)")
ax2.set_ylabel(r"Average Degree of Consolidation, $U$ (%)")
ax2.set_xlim(left=min(t_log), right=max(time_values))
ax2.set_ylim(0, 20)

# Applying Log X-Scale consistent with the theme's time treatment
ax2.set_xscale('log')
ax2.margins(x=0)

# Legend placed outside at the bottom
ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)

plt.tight_layout()
plt.subplots_adjust(bottom=0.25)
save_smart('output/plots/degree_of_consolidation_comparison')
plt.show()