#include "LargeStrainMechanicsAD.h"

registerMooseObject("terzaghi_projectApp", LargeStrainMechanicsAD);

InputParameters
LargeStrainMechanicsAD::validParams()
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

LargeStrainMechanicsAD::LargeStrainMechanicsAD(const InputParameters & params)
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
LargeStrainMechanicsAD::computeQpResidual()
{
  // 1) Construct Deformation Gradient F (Assuming 2D Plane Strain)
  ADRankTwoTensor F;
  F(0,0) = 1.0 + _grad_ux[_qp](0);
  F(0,1) = _grad_ux[_qp](1);
  F(1,0) = _grad_uy[_qp](0);
  F(1,1) = 1.0 + _grad_uy[_qp](1);
  F(2,2) = 1.0; 

  ADReal J = F.det();
  ADRankTwoTensor C = F.transpose() * F; 
  ADRankTwoTensor C_inv = C.inverse();

  // 2) Compute Green-Lagrange Strain E = 0.5 * (C - I)
  ADRankTwoTensor E = 0.5 * (C - ADRankTwoTensor::Identity());

  // 3) St. Venant-Kirchhoff Material (Effective PK2 Stress)
  // S' = lambda * tr(E) * I + 2 * mu * E
  ADReal trE = E.trace();
  ADRankTwoTensor S_prime = E * (2.0 * _mu);
  S_prime.addIa(trE * _lambda); 

  // 4) Total PK2 Stress (Pull back the pore pressure)
  // S_total = S' - alpha * U * J * C^-1
  ADRankTwoTensor S_total = S_prime - C_inv * (_alpha * _p[_qp] * J);

  // 5) Convert to First Piola-Kirchhoff Stress (P = F * S_total)
  ADRankTwoTensor P = F * S_total;

  // 6) Return the weak form residual: P_ij * test_i,j
  // We extract the row corresponding to the active component
  ADRealVectorValue P_row(P(_comp, 0), P(_comp, 1), P(_comp, 2));

  return P_row * _grad_test[_i][_qp];
}