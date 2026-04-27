#include "SmallStrainDiffusionAndStorageAD.h"

registerMooseObject("terzaghi_projectApp", SmallStrainDiffusionAndStorageAD);

InputParameters
SmallStrainDiffusionAndStorageAD::validParams()
{
  InputParameters params = ADTimeKernel::validParams();
  params.addRequiredParam<Real>("kappa_mu", "Mobility (Permeability / Viscosity)");
  params.addRequiredParam<Real>("m_v", "Volume compressibility (Storage coefficient)");
  return params;
}

SmallStrainDiffusionAndStorageAD::SmallStrainDiffusionAndStorageAD(const InputParameters & params)
  : ADTimeKernel(params),
    _kappa_mu(getParam<Real>("kappa_mu")),
    _m_v(getParam<Real>("m_v"))
{
}

ADReal
SmallStrainDiffusionAndStorageAD::computeQpResidual()
{
  // Fluid Storage: psi * m_v * p_dot
  ADReal storage_term = _test[_i][_qp] * _m_v * _u_dot[_qp];

  // Darcy Flow: grad_psi * (k/mu * grad_p)
  ADReal darcy_term = _grad_test[_i][_qp] * (_kappa_mu * _grad_u[_qp]);

  return storage_term + darcy_term;
}