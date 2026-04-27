#include "VoidRatioAux.h"

registerMooseObject("terzaghi_projectApp", VoidRatioAux);

InputParameters
VoidRatioAux::validParams()
{
  InputParameters params = AuxKernel::validParams();
  params.addRequiredParam<Real>("e0", "Initial void ratio");
  params.addRequiredCoupledVar("u_x", "Displacement in x");
  params.addRequiredCoupledVar("u_y", "Displacement in y");
  return params;
}

VoidRatioAux::VoidRatioAux(const InputParameters & parameters)
  : AuxKernel(parameters),
    _e0(getParam<Real>("e0")),
    _grad_ux(coupledGradient("u_x")),
    _grad_uy(coupledGradient("u_y"))
{
}

Real
VoidRatioAux::computeValue()
{
  // Reconstruct J = det(F) just like in your main kernel
  Real F00 = 1.0 + _grad_ux[_qp](0);
  Real F01 = _grad_ux[_qp](1);
  Real F10 = _grad_uy[_qp](0);
  Real F11 = 1.0 + _grad_uy[_qp](1);

  Real J = (F00 * F11) - (F01 * F10);
  
  // e = J*(1 + e0) - 1
  return J * (1.0 + _e0) - 1.0;
}