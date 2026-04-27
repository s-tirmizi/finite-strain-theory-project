#include "SmallStrainMechanicsAD.h"

registerMooseObject("terzaghi_projectApp", SmallStrainMechanicsAD);

InputParameters
SmallStrainMechanicsAD::validParams()
{
  InputParameters params = ADKernel::validParams();
  params.addRequiredParam<Real>("lambda", "Lame's first parameter");
  params.addRequiredParam<Real>("mu", "Lame's second parameter");
  params.addRequiredParam<Real>("alpha", "Biot coefficient");
  params.addRequiredParam<unsigned int>("component", "0 for x-component, 1 for y-component");

  params.addRequiredCoupledVar("u_x", "Displacement in x");
  params.addRequiredCoupledVar("u_y", "Displacement in y");
  params.addRequiredCoupledVar("p", "Pore pressure");

  return params;
}

SmallStrainMechanicsAD::SmallStrainMechanicsAD(const InputParameters & params)
  : ADKernel(params),
    _lambda(getParam<Real>("lambda")),
    _mu(getParam<Real>("mu")),
    _alpha(getParam<Real>("alpha")),
    _comp(getParam<unsigned int>("component")),
    _p(adCoupledValue("p")),
    _grad_ux(adCoupledGradient("u_x")),
    _grad_uy(adCoupledGradient("u_y"))
{
  if (_comp > 1)
    mooseError("Component must be 0 (x) or 1 (y) for 2D.");
}

ADReal
SmallStrainMechanicsAD::computeQpResidual()
{
  // 1) Compute Infinitesimal Strain Tensor components
  ADReal eps_xx = _grad_ux[_qp](0);
  ADReal eps_yy = _grad_uy[_qp](1);
  ADReal eps_xy = 0.5 * (_grad_ux[_qp](1) + _grad_uy[_qp](0));
  
  ADReal tr_eps = eps_xx + eps_yy;

  // 2) Compute Effective Cauchy Stress (Linear Elasticity)
  ADReal sig_prime_xx = _lambda * tr_eps + 2.0 * _mu * eps_xx;
  ADReal sig_prime_yy = _lambda * tr_eps + 2.0 * _mu * eps_yy;
  ADReal sig_prime_xy = 2.0 * _mu * eps_xy;

  // 3) Construct Total Stress Row for the active component
  ADRealVectorValue stress_row;
  
  if (_comp == 0) // x-component
  {
    stress_row(0) = sig_prime_xx - _alpha * _p[_qp];
    stress_row(1) = sig_prime_xy;
    stress_row(2) = 0.0;
  }
  else // y-component
  {
    stress_row(0) = sig_prime_xy;
    stress_row(1) = sig_prime_yy - _alpha * _p[_qp];
    stress_row(2) = 0.0;
  }

  // 4) Return the weak form residual: sigma_ij * test_i,j
  return stress_row * _grad_test[_i][_qp];
}