import pyvista as pv
import matplotlib.pyplot as plt
import numpy as np
import vtk

# This disables the pop-up and terminal error reporting for VTK
vtk.vtkObject.GlobalWarningDisplayOff()
pv.set_error_output_file('vtk_errors.log')

# 1. Setup specific times to plot (in days) matching the Exodus sync_times
times_days = [730.0, 1606.0, 2518.0, 3248.0]
time_labels = ['0.0yr', '2.0yr', '4.4yr', '6.9yr', '8.9yr']

# 2. Initialize PyVista Exodus readers for both Large and Small strain
# (Ensure these file paths match your actual .e output names)
ls_reader = pv.get_reader('output/bilayer_large_strain_load_-1.e')
ss_reader = pv.get_reader('output/bilayer_small_strain_load_-1.e')

# Adjust figure size to accommodate the outside legend
plt.figure(figsize=(9, 6)) 

# Generate gradients for the isochrones (Reds for LS, Blues for SS)
colors_ls = plt.cm.Reds(np.linspace(0.9, 0.3, len(times_days)))
colors_ss = plt.cm.Blues(np.linspace(0.9, 0.3, len(times_days)))

# 3. Iterative Plotting
for t_day, label, c_ls, c_ss in zip(times_days, time_labels, colors_ls, colors_ss):
    
    # Setup the closest time values
    ls_reader.set_active_time_value(t_day)
    ss_reader.set_active_time_value(t_day)
    
    ls_mesh = ls_reader.read()
    ss_mesh = ss_reader.read()
    
    # Combine blocks
    if isinstance(ls_mesh, pv.MultiBlock):
        ls_mesh = ls_mesh.combine()
    if isinstance(ss_mesh, pv.MultiBlock):
        ss_mesh = ss_mesh.combine()
        
    # Extract points along a vertical profile (at x = 0.0)
    start_point = [0.0, 0.0, 0.0]
    end_point = [0.0, 5.0, 0.0]
    
    ls_line = ls_mesh.sample_over_line(start_point, end_point, resolution=200)
    ss_line = ss_mesh.sample_over_line(start_point, end_point, resolution=200)
    
    # Calculate Depth (Depth = 5.0m - Y coordinate)
    ls_depth = 5.0 - ls_line.points[:, 1]
    ss_depth = 5.0 - ss_line.points[:, 1]
    
    # Excess pore pressure 'p'
    ls_p = ls_line.point_data['p']
    ss_p = ss_line.point_data['p']
    
    # Plot Small Strain (Dashed lines, Blue gradient)
    plt.plot(ss_p, ss_depth, linestyle='--', color=c_ss, linewidth=2.0, label=f'SS ({label})')

    # Plot Large Strain (Solid lines, Red gradient)
    plt.plot(ls_p, ls_depth, linestyle='-', color=c_ls, linewidth=2.5, label=f'LS ({label})')

# 4. Annotations and Formatting
# Layer interface line (At Depth = 2.0m, since Y=3.0m)
plt.axhline(y=2.0, color='grey', linestyle='--', linewidth=1.5)

# Subtle background shading to distinguish layers mapped to depth
plt.fill_betweenx([0, 2], 0, 160, alpha=0.04, color='seagreen')   # Soft Layer: Depth 0m to 2m
plt.fill_betweenx([2, 5], 0, 160, alpha=0.04, color='steelblue')  # Stiff Layer: Depth 2m to 5m

# Text labels for layers positioned at specific depths
plt.text(85, 1.0, 'Layer 1\n(soft)', color='seagreen', ha='center', va='center', fontsize=10)
plt.text(85, 3.5, 'Layer 2\n(stiff)', color='steelblue', ha='center', va='center', fontsize=10)

# Axis labels and limits
plt.xlabel('Excess Pore Pressure (kPa)', fontsize=12)
plt.ylabel('Depth (m)', fontsize=12)
plt.title('Comparison: Large Strain vs. Small Strain Isochrones', fontsize=14)
plt.xlim(0, 155) 
plt.ylim(0, 5.0) 

# Invert Y-axis so Depth 0 is at the top!
plt.gca().invert_yaxis()

# Grid and Legend
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9, framealpha=0.9)

plt.tight_layout()
plt.savefig('output/strain_comparison_isochrones_-1.png', dpi=300, bbox_inches='tight')
plt.show()