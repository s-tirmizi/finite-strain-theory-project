#pragma once

#include "ADKernel.h"

class SmallStrainMechanicsAD : public ADKernel
{
public:
  static InputParameters validParams();
  SmallStrainMechanicsAD(const InputParameters & params);

protected:
  virtual ADReal computeQpResidual() override;

  const Real _lambda;
  const Real _mu;
  const Real _alpha;
  const unsigned int _comp;

  const ADVariableValue & _p;
  const ADVariableGradient & _grad_ux;
  const ADVariableGradient & _grad_uy;
};