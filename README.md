# finite-strain-theory-project
PGE 383 - Advanced Geomechanics Course Project

# Beyond Small Strain: Proving the Importance of Finite Strain Theory
**1D Terzaghi Consolidation: A Computational Comparison of Small-Strain and Total Lagrangian Formulations**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Status: Active](https://img.shields.io/badge/Status-Active-success.svg)]()

## 📖 Project Overview
In classical geomechanics, Terzaghi's 1D consolidation theory is often implemented under the assumption of infinitesimal strain, where the soil geometry and material properties remain static. However, for soft soils undergoing massive loading, these assumptions break down. 

This repository houses the computational framework for my course project, **"Beyond Small Strain."** It demonstrates exactly *why* and *when* finite strain theory is required by comparing a standard small-strain poroelastic model against a fully coupled, Total Lagrangian large-strain model.

By mapping finite deformations back to a reference configuration, the large-strain model accurately captures dynamic void ratios, deformation-dependent permeability, and geometric non-linearities that small-strain models ignore.

## ✨ Key Features & Models

This repository analyzes a complete 2x2 test matrix to isolate the effects of finite strain kinematics and soil stratigraphy:

* **Homogeneous Models (Small vs. Large Strain):** Establishes the baseline differences between constant permeability/static geometry and deformation-dependent permeability/dynamic void ratios in a uniform 10m soil column.
* **Bilayer Models (Small vs. Large Strain):** Simulates a complex stratigraphy (Soft Clay over Stiff Clay) to demonstrate how finite strain theory captures the severe non-linear compression of soft upper layers missed by infinitesimal assumptions.
* **Coupling Architectures:** Explores the computational trade-offs between partially coupled (small-strain) and fully coupled (large-strain Total Lagrangian) fluid-solid interactions.
### 3. Analytical Validation
* Includes the classical 1D Terzaghi analytical series solution (Fourier sine series) to validate the numerical solver's initial excess pore water pressure dissipation.

## 🧮 Numerical Strategy
The governing systems of partial differential equations (Solid Equilibrium + Fluid Mass Conservation) are solved using:
* **Solver:** Preconditioned Jacobian-Free Newton-Krylov (PJFNK) with automatic scaling.
* **Linear Algebra:** MUMPS parallel direct solver.
* **Time Integration:** Implicit Euler scheme for unconditional stability.
* **Time-Stepping:** Iteration-adaptive time-stepping to accurately resolve the rapid pore pressure generation during the initial loading phase.

## 📂 Repository Structure
```text
├── docs/                   # Mathematical documentation and weak form derivations
├── meshes/                 # Quad9 mesh files for the 1D columns
├── src/
│   ├── analytical/         # Python/MATLAB scripts for the Terzaghi series solution
│   ├── small_strain/       # Input files and kernels for the small-strain bilayer model
│   └── large_strain/       # Input files and kernels for the Total Lagrangian model
├── results/                # Output data, paraview files, and comparative plots
└── README.md
