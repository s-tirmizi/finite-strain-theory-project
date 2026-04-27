#include "LargeStrainBiotDivergenceAD.h"
#include "terzaghi_projectApp.h"

registerMooseObject("terzaghi_projectApp", LargeStrainBiotDivergenceAD);

InputParameters
LargeStrainBiotDivergenceAD::validParams()
{
  InputParameters params = ADTimeKernel::validParams();
  params.addRequiredParam<Real>("alpha", "Biot coefficient");
  params.addRequiredCoupledVar("u_x", "Displacement X–component");
  params.addRequiredCoupledVar("u_y", "Displacement Y–component");
  params.set<MultiMooseEnum>("matrix_tags") = "system";
  return params;
}

LargeStrainBiotDivergenceAD::LargeStrainBiotDivergenceAD(const InputParameters & p)
  : ADTimeKernel(p),
    _B(p.get<Real>("alpha")),
    _grad_ux(adCoupledGradient("u_x")),
    _grad_uy(adCoupledGradient("u_y")),
    _u_x_dot(adCoupledDot("u_x")), 
    _u_y_dot(adCoupledDot("u_y")), 
    _grad_u_x_dot(adCoupledGradientDot("u_x")),
    _grad_u_y_dot(adCoupledGradientDot("u_y"))
{}

ADReal
LargeStrainBiotDivergenceAD::computeQpResidual()
{
  // 1) Construct Deformation Gradient F
  ADReal F00 = 1.0 + _grad_ux[_qp](0);
  ADReal F01 = _grad_ux[_qp](1);
  ADReal F10 = _grad_uy[_qp](0);
  ADReal F11 = 1.0 + _grad_uy[_qp](1);

  // 2) Construct Rate of Deformation Gradient F_dot
  ADReal Fdot00 = _grad_u_x_dot[_qp](0);
  ADReal Fdot01 = _grad_u_x_dot[_qp](1);
  ADReal Fdot10 = _grad_u_y_dot[_qp](0);
  ADReal Fdot11 = _grad_u_y_dot[_qp](1);

  // 3) Calculate large-strain volumetric rate analytically
  // J_dot = d/dt (det(F))
  ADReal J_dot = Fdot00 * F11 + F00 * Fdot11 - Fdot01 * F10 - F01 * Fdot10;

  // 4) Return true finite-strain coupling residual
  // Residual: ∫ \psi_i [ B * J_dot ] dV_0
  return _B * J_dot * _test[_i][_qp];
}