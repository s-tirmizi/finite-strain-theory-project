#pragma once
#include "AuxKernel.h"

class PermeabilityAux : public AuxKernel
{
public:
  static InputParameters validParams();
  PermeabilityAux(const InputParameters & parameters);

protected:
  virtual Real computeValue() override;

  Real _k0_mu;
  Real _e0;
  const VariableGradient & _grad_ux;
  const VariableGradient & _grad_uy;
};