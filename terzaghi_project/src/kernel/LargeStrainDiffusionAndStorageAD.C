#include "LargeStrainDiffusionAndStorageAD.h"

registerMooseObject("terzaghi_projectApp", LargeStrainDiffusionAndStorageAD);

InputParameters
LargeStrainDiffusionAndStorageAD::validParams()
{
  InputParameters params = ADTimeKernel::validParams();
  params.addRequiredParam<Real>("initial_kappa_mu", "Initial Mobility (k0 / mu)");
  params.addRequiredParam<Real>("m_v", "Volume compressibility");
  params.addRequiredParam<Real>("e0", "Initial void ratio of the soil");
  
  params.addRequiredCoupledVar("u_x", "Displacement in x");
  params.addRequiredCoupledVar("u_y", "Displacement in y");
  return params;
}

LargeStrainDiffusionAndStorageAD::LargeStrainDiffusionAndStorageAD(const InputParameters & params)
  : ADTimeKernel(params),
    _k0_mu(getParam<Real>("initial_kappa_mu")),
    _m_v(getParam<Real>("m_v")),
    _e0(getParam<Real>("e0")),
    _grad_ux(adCoupledGradient("u_x")),
    _grad_uy(adCoupledGradient("u_y"))
{
}

ADReal
LargeStrainDiffusionAndStorageAD::computeQpResidual()
{
  // 1) Construct F and its inverse
  ADRankTwoTensor F;
  F(0,0) = 1.0 + _grad_ux[_qp](0);
  F(0,1) = _grad_ux[_qp](1);
  F(1,0) = _grad_uy[_qp](0);
  F(1,1) = 1.0 + _grad_uy[_qp](1);
  F(2,2) = 1.0;

  ADReal J = F.det();
  ADRankTwoTensor F_inv = F.inverse();

  // 2) Calculate Current Void Ratio (e)
  // J = V/V0 = (1 + e) / (1 + e0)  =>  e = J*(1 + e0) - 1
  ADReal e_curr = J * (1.0 + _e0) - 1.0;

  // 3) Kozeny-Carman Permeability Update
  // k = k0 * [ (e^3 / (1+e)) / (e0^3 / (1+e0)) ]
  // We add a tiny floor value to prevent permeability from going to exactly 0 or negative during Newton iterations
  ADReal e_safe = std::max(e_curr, ADReal(0.01)); 
  
  ADReal kc_multiplier = (e_safe * e_safe * e_safe / (1.0 + e_safe)) / 
                         (_e0 * _e0 * _e0 / (1.0 + _e0));

  ADReal current_kappa_mu = _k0_mu * kc_multiplier;

  // 4) Pulled-back Permeability tensor: K_TL = F^-1 * F^-T * (J * current_k/mu)
  ADRankTwoTensor K_TL = F_inv * F_inv.transpose() * (J * current_kappa_mu);

  // 5) Calculate components
  ADReal storage_term = _test[_i][_qp] * J * _m_v * _u_dot[_qp];
  ADReal darcy_term = _grad_test[_i][_qp] * (K_TL * _grad_u[_qp]);

  return storage_term + darcy_term;
}