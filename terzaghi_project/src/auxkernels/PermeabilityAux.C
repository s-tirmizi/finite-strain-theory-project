#include "PermeabilityAux.h"
#include <algorithm>

registerMooseObject("terzaghi_projectApp", PermeabilityAux);

InputParameters
PermeabilityAux::validParams()
{
  InputParameters params = AuxKernel::validParams();
  params.addRequiredParam<Real>("initial_kappa_mu", "Initial Mobility");
  params.addRequiredParam<Real>("e0", "Initial void ratio");
  params.addRequiredCoupledVar("u_x", "Displacement in x");
  params.addRequiredCoupledVar("u_y", "Displacement in y");
  return params;
}

PermeabilityAux::PermeabilityAux(const InputParameters & parameters)
  : AuxKernel(parameters),
    _k0_mu(getParam<Real>("initial_kappa_mu")),
    _e0(getParam<Real>("e0")),
    _grad_ux(coupledGradient("u_x")),
    _grad_uy(coupledGradient("u_y"))
{
}

Real
PermeabilityAux::computeValue()
{
  Real F00 = 1.0 + _grad_ux[_qp](0);
  Real F01 = _grad_ux[_qp](1);
  Real F10 = _grad_uy[_qp](0);
  Real F11 = 1.0 + _grad_uy[_qp](1);

  Real J = (F00 * F11) - (F01 * F10);
  Real e_curr = J * (1.0 + _e0) - 1.0;
  Real e_safe = std::max(e_curr, 0.01);
  
  Real kc_multiplier = (e_safe * e_safe * e_safe / (1.0 + e_safe)) / 
                       (_e0 * _e0 * _e0 / (1.0 + _e0));

  return _k0_mu * kc_multiplier;
}