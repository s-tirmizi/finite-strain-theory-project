[Mesh]
  [gen]
    type       = GeneratedMeshGenerator
    dim        = 2
    nx         = 1
    ny         = 300
    xmin       = 0.0
    xmax       = 1.0 
    ymin       = 0.0
    ymax       = 5.0      # Total height H = 5m
    elem_type  = QUAD9
  []
  [layer1_soft]
    type        = SubdomainBoundingBoxGenerator
    input       = gen
    bottom_left = '0.0 3.0 0.0'
    top_right   = '1.0 5.0 0.0'
    block_id    = 1       # Layer 1: z = 3 to 5m
  []
  [layer2_stiff]
    type        = SubdomainBoundingBoxGenerator
    input       = layer1_soft
    bottom_left = '0.0 0.0 0.0'
    top_right   = '1.0 3.0 0.0'
    block_id    = 2       # Layer 2: z = 0 to 3m
  []
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
    # Ramps near-instantaneously to prevent drainage during loading
    value = '-1 * min(t/0.01, 1.0)'
  [../]
[]

[Kernels]
  # ==========================================
  # LAYER 1: SOFT CLAY (Block 1)
  # ==========================================
  [./mech_x_L1]
    type             = SmallStrainMechanicsAD
    variable         = u_x     
    block            = 1
    p                = p       
    u_x              = u_x     
    u_y              = u_y     
    lambda           = 0.0     
    mu               = 362.25  # Derived from Cc=1.0, e0=2.5, stress=90kPa
    alpha            = 1.0
    component        = 0
  [../]
  [./mech_y_L1]
    type             = SmallStrainMechanicsAD
    variable         = u_y     
    block            = 1
    p                = p       
    u_x              = u_x     
    u_y              = u_y     
    lambda           = 0.0 
    mu               = 362.25  
    alpha            = 1.0
    component        = 1
  [../]
  [./p_diffusion_L1]
    type             = SmallStrainDiffusionAndStorageAD
    variable         = p
    block            = 1
    kappa_mu         = 1e-6    
    m_v              = 0.0     # Set to 0: Storage is fully handled by Biot divergence
  [../]

  # ==========================================
  # LAYER 2: STIFF CLAY (Block 2)
  # ==========================================
  [./mech_x_L2]
    type             = SmallStrainMechanicsAD
    variable         = u_x     
    block            = 2
    p                = p       
    u_x              = u_x     
    u_y              = u_y     
    lambda           = 0.0     
    mu               = 1293.75 # Derived from Cc=0.12, e0=0.5, stress=90kPa
    alpha            = 1.0
    component        = 0
  [../]
  [./mech_y_L2]
    type             = SmallStrainMechanicsAD
    variable         = u_y     
    block            = 2
    p                = p       
    u_x              = u_x     
    u_y              = u_y     
    lambda           = 0.0 
    mu               = 1293.75  
    alpha            = 1.0
    component        = 1
  [../]
  [./p_diffusion_L2]
    type             = SmallStrainDiffusionAndStorageAD
    variable         = p
    block            = 2
    kappa_mu         = 1e-7    # Adjusted to match the multi-year large strain curve
    m_v              = 0.0     # Set to 0: Storage is fully handled by Biot divergence
  [../]

  # ==========================================
  # GLOBAL KERNELS (Applied to all blocks)
  # ==========================================
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
  end_time = 3250.0          # Extended to ~8.9 years
  
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
    sync_times = '0.01 730.0 1606.0 2518.0 3248.0'
    sync_only = true
    file_base = './output/bilayer_small_strain_load_-1'
  [../]
[]