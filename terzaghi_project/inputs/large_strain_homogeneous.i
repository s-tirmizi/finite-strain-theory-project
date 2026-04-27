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

[AuxVariables]
  [./void_ratio]
    order = CONSTANT
    family = MONOMIAL
  [../]
  [./permeability]
    order = CONSTANT
    family = MONOMIAL
  [../]
[]

[AuxKernels]
  # ----- LAYER 1 -----
  [./void_ratio_L1]
    type = VoidRatioAux
    variable = void_ratio
    e0 = 0.8
    u_x = u_x
    u_y = u_y
  [../]
  [./perm_L1]
    type = PermeabilityAux
    variable = permeability
    initial_kappa_mu = 1e-6
    e0 = 0.8
    u_x = u_x
    u_y = u_y
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
    value = '-500 * min(t/1.0, 1.0)'
  [../]
[]

[Kernels]
  # --- Solid Mechanics Equilibrium ---
  [./mech_x]
    type             = LargeStrainMechanicsAD
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
    type             = LargeStrainMechanicsAD
    variable         = u_y     
    p                = p       
    u_x              = u_x     
    u_y              = u_y     
    lambda           = 0.0 
    mu               = 2000.0  
    alpha            = 1.0
    component        = 1
  [../]

  # --- Fluid Flow & Consolidation ---
  [./p_diffusion]
    type        = LargeStrainDiffusionAndStorageAD
    variable    = p
    u_x         = u_x
    u_y         = u_y
    initial_kappa_mu = 1e-6   # Standard initial permeability
    m_v         = 1e-7   
    e0          = 0.8         # Initial void ratio (e.g., highly compressible clay)
    #kappa_mu    = 1e-6    # m^2/(kPa*day) to yield Cv = 0.01
  [../]

  [./biot_div_ad]
    type        = LargeStrainBiotDivergenceAD
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
  automatic_scaling = true
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
    file_base = './output/large_strain_load_-500'
  [../]
[]