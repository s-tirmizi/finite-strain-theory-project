[Mesh]
  type       = GeneratedMesh
  dim        = 2
  nx         = 1
  ny         = 300
  xmin       = 0.0
  xmax       = 1.0 
  ymin       = 0.0
  ymax       = 10.0
  elem_type  = QUAD9
[]

[Variables]
  [./p]
    family = LAGRANGE
    order  = FIRST
  [../]
  [./u_x]
    family = LAGRANGE
    order  = SECOND
  [../]
  [./u_y]
    family = LAGRANGE
    order  = SECOND
  [../]
[]

[ICs]
  [./p_ic]
    type     = ConstantIC
    variable = p
    value    = 0.0
  [../]
  [./u_x_ic]
    type     = ConstantIC
    variable = u_x
    value    = 0.0
  [../]
  [./u_y_ic]
    type     = ConstantIC
    variable = u_y
    value    = 0.0
  [../] 
[]

[Functions]
  [./top_traction]
    type  = ParsedFunction
    # Ramps linearly from 0 to -1e6 over the first 1.0 day, then holds constant
    #value = '-4e2 * min(t/1.0, 1.0)' 
    value = '-100 * min(t/1.0, 1.0)'
  [../]
[]

[Kernels]
  # --- Solid Mechanics Equilibrium (Small Strain) ---
  [./mech_x]
    type             = SmallStrainMechanicsAD
    variable         = u_x     
    p                = p       
    u_x              = u_x     
    u_y              = u_y     
    lambda           = 0.0     # Tuned to match constrained 1D modulus
    mu               = 2000.0  # M = lambda + 2*mu = 10,000 kPa
    alpha            = 1.0
    component        = 0
  [../]
  [./mech_y]
    type             = SmallStrainMechanicsAD
    variable         = u_y     
    p                = p       
    u_x              = u_x     
    u_y              = u_y     
    lambda           = 0.0 
    mu               = 2000.0  
    alpha            = 1.0
    component        = 1
  [../]

  # --- Fluid Flow & Consolidation (Small Strain) ---
  [./p_diffusion]
    type        = SmallStrainDiffusionAndStorageAD
    variable    = p
    kappa_mu    = 1e-6    # m^2/(kPa*day) to yield Cv = 0.01
    m_v         = 1e-7    # Slight numerical compressibility
  [../]
  [./biot_div_ad]
    type        = SmallStrainBiotDivergenceAD
    variable    = p
    alpha       = 1.0
    u_x         = u_x
    u_y         = u_y
  [../]
[]

[BCs]
  # Roller boundaries for 1D column constraint
  [./fix_ux_left_right]
    type     = DirichletBC
    variable = u_x
    boundary = 'left right'
    value    = 0.0
  [../]
  
  # Impermeable rigid base
  [./fix_uy_bottom]
    type     = DirichletBC
    variable = u_y
    boundary = bottom
    value    = 0.0
  [../]
  
  # Drained top boundary
  [./p_drain]
    type     = DirichletBC
    variable = p
    boundary = top
    value    = 0.0
  [../]
  
  # Surcharge load
  [./top_load]
    type     = FunctionNeumannBC
    variable = u_y
    boundary = top
    function = top_traction
  [../]
[]

[Preconditioning]
  [./smp]
    type = SMP
    full = true
  [../]
[]

[Executioner]
  type = Transient
  scheme = 'IMPLICIT-EULER'
  start_time = 0.0
  end_time = 365.0
  
  nl_abs_tol = 1e-8
  nl_rel_tol = 1e-6
  
  l_max_its = 15 
  line_search = basic
  
  # MUMPS parallel direct solver
  petsc_options_iname = '-pc_type -pc_factor_mat_solver_type'
  petsc_options_value = 'lu       mumps'

  [./TimeStepper]
    type = IterationAdaptiveDT
    dt = 0.001                 # Start tiny to catch the undrained spike
    cutback_factor = 0.5     
    growth_factor = 1.5      
    optimal_iterations = 6   
    iteration_window = 2     
  [../]
[]

[Outputs]
  [.exodus]
    type = Exodus
    sync_times = '1.0 10.0 30.0 100.0 365.0'
    sync_only = true
    file_base = './output/small_strain_load_-100'
  [../]
[]