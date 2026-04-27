#include "SmallStrainBiotDivergenceAD.h"
#include "terzaghi_projectApp.h"

registerMooseObject("terzaghi_projectApp", SmallStrainBiotDivergenceAD);

InputParameters
SmallStrainBiotDivergenceAD::validParams()
{
  InputParameters params = ADTimeKernel::validParams();
  params.addRequiredParam<Real>("alpha", "Biot coefficient");
  params.addRequiredCoupledVar("u_x", "Displacement X-component");
  params.addRequiredCoupledVar("u_y", "Displacement Y-component");
  return params;
}

SmallStrainBiotDivergenceAD::SmallStrainBiotDivergenceAD(const InputParameters & p)
  : ADTimeKernel(p),
    _B(p.get<Real>("alpha")),
    _u_x_dot(adCoupledDot("u_x")), 
    _u_y_dot(adCoupledDot("u_y")), 
    _grad_u_x_dot(adCoupledGradientDot("u_x")),
    _grad_u_y_dot(adCoupledGradientDot("u_y"))
{}

ADReal
SmallStrainBiotDivergenceAD::computeQpResidual()
{
  // Small-strain volumetric rate: div(u_dot) = dux_dot/dx + duy_dot/dy
  ADReal div_u_dot = _grad_u_x_dot[_qp](0) + _grad_u_y_dot[_qp](1);

  // Residual: \psi_i * alpha * div(u_dot)
  return _test[_i][_qp] * _B * div_u_dot;
}