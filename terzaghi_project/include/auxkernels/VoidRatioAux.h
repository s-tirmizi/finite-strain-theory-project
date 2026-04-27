#pragma once
#include "AuxKernel.h"

class VoidRatioAux : public AuxKernel
{
public:
  static InputParameters validParams();
  VoidRatioAux(const InputParameters & parameters);

protected:
  virtual Real computeValue() override;

  Real _e0;
  const VariableGradient & _grad_ux;
  const VariableGradient & _grad_uy;
};