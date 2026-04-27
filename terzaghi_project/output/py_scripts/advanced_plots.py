import pyvista as pv
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.lines import Line2D
import numpy as np
import vtk
import os
import shutil
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
ls_reader = pv.get_reader('output/bilayer_large_strain_load_-1.e')
ss_reader = pv.get_reader('output/bilayer_small_strain_load_-1.e')

# ==========================================
# 4. FIGURE 1: Isochrones Comparison
# ==========================================
print("Processing Figure 1: Isochrones...")
times_days = [730.0, 1606.0, 2518.0, 3248.0]
time_labels = ['2.0yr', '4.4yr', '6.9yr', '8.9yr'] # Matched lengths

fig1, ax1 = plt.subplots(figsize=(8, 6))

colors_ls = plt.cm.Reds(np.linspace(0.4, 0.9, len(times_days)))
colors_ss = plt.cm.Blues(np.linspace(0.4, 0.9, len(times_days)))

for t_day, label, c_ls, c_ss in zip(times_days, time_labels, colors_ls, colors_ss):
    ls_reader.set_active_time_value(t_day)
    ss_reader.set_active_time_value(t_day)
    
    ls_mesh = ls_reader.read()
    ss_mesh = ss_reader.read()
    
    if isinstance(ls_mesh, pv.MultiBlock): ls_mesh = ls_mesh.combine()
    if isinstance(ss_mesh, pv.MultiBlock): ss_mesh = ss_mesh.combine()
        
    start_point, end_point = [0.0, 0.0, 0.0], [0.0, 5.0, 0.0]
    ls_line = ls_mesh.sample_over_line(start_point, end_point, resolution=200)
    ss_line = ss_mesh.sample_over_line(start_point, end_point, resolution=200)
    
    ls_depth = 5.0 - ls_line.points[:, 1]
    ss_depth = 5.0 - ss_line.points[:, 1]
    
    ls_p = ls_line.point_data['p']
    ss_p = ss_line.point_data['p']
    
    ax1.plot(ss_p, ss_depth, linestyle='--', color=c_ss, linewidth=2)
    ax1.plot(ls_p, ls_depth, linestyle='-', color=c_ls, linewidth=2)

# Subsurface Layer Shading
ax1.axhline(y=2.0, color='grey', linestyle='--', linewidth=1.5)
ax1.fill_betweenx([0, 2], 0, 2, alpha=0.08, color='seagreen')  
ax1.fill_betweenx([2, 5], 0, 2, alpha=0.08, color='steelblue') 
ax1.text(0.6, 1.0, 'Layer 1\n(soft)', color='seagreen', ha='center', va='center', fontsize=14, weight='bold')
ax1.text(0.6, 3.5, 'Layer 2\n(stiff)', color='steelblue', ha='center', va='center', fontsize=14, weight='bold')

ax1.set_xlabel(r"Excess Pore Pressure, $\Delta u$ (kPa)")
ax1.set_ylabel(r"Depth, $z$ (m)")
ax1.set_xlim(0, 1.5) 
ax1.set_ylim(0, 5.0) 
ax1.invert_yaxis()
ax1.margins(x=0)

# Custom legend placed outside
model_handles = [
    Line2D([0], [0], color='tab:red', linestyle='-', linewidth=2, label='Large Strain'),
    Line2D([0], [0], color='tab:blue', linestyle='--', linewidth=2, label='Small Strain')
]
time_handles = [
    Line2D([0], [0], color='black', alpha=0.6, linewidth=2, label=f'{lbl}') 
    for lbl in time_labels
]

legend1 = ax1.legend(handles=model_handles, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)
ax1.add_artist(legend1)
ax1.legend(handles=time_handles, loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=4)

plt.tight_layout()
plt.subplots_adjust(bottom=0.35)
save_smart('output/plots/bilayer_strain_comparison_isochrones_-1')
plt.show()


# ==========================================
# 5. FIGURE 2: Average Degree of Consolidation
# ==========================================
print("Processing Figure 2: Degree of Consolidation...")
times_ls = np.array(ls_reader.time_values)
times_ss = np.array(ss_reader.time_values)

years_ls = times_ls / 365.25
years_ss = times_ss / 365.25

avg_p_ls = np.zeros(len(times_ls))
avg_p_ss = np.zeros(len(times_ss))

for i, t in enumerate(times_ls):
    ls_reader.set_active_time_value(t)
    mesh = ls_reader.read()
    if isinstance(mesh, pv.MultiBlock): mesh = mesh.combine()
    avg_p_ls[i] = np.mean(mesh.point_data['p'])

for i, t in enumerate(times_ss):
    ss_reader.set_active_time_value(t)
    mesh = ss_reader.read()
    if isinstance(mesh, pv.MultiBlock): mesh = mesh.combine()
    avg_p_ss[i] = np.mean(mesh.point_data['p'])

p0_ls = np.max(avg_p_ls)
p0_ss = np.max(avg_p_ss)

U_ls = (1.0 - (avg_p_ls / p0_ls)) * 100.0
U_ss = (1.0 - (avg_p_ss / p0_ss)) * 100.0

fig2, ax2 = plt.subplots(figsize=(8, 6))

ax2.plot(years_ls, U_ls, color='tab:red', linestyle='-', linewidth=2, label='Large Strain (Gibson)')
ax2.plot(years_ss, U_ss, color='tab:blue', linestyle='--', linewidth=2, label='Small Strain (Terzaghi)')

ax2.set_xlabel(r"Time (years)")
ax2.set_ylabel(r"Degree of Consolidation, $U$ (%)")
ax2.set_xlim(0, 8.7)
ax2.set_ylim(0, 105)
ax2.margins(x=0)

ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)

plt.tight_layout()
plt.subplots_adjust(bottom=0.25)
save_smart('output/plots/bilayer_degree_of_consolidation_-1')
plt.show()