#pragma once

#include "ADKernel.h"
#include "RankTwoTensor.h"

class LargeStrainMechanicsAD : public ADKernel
{
public:
  static InputParameters validParams();
  LargeStrainMechanicsAD(const InputParameters & parameters);

protected:
  virtual ADReal computeQpResidual() override;

  const Real _lambda;
  const Real _mu;
  const Real _alpha;
  const unsigned int _comp; // 0 for x, 1 for y

  const ADVariableValue & _p;
  const ADVariableGradient & _grad_ux;
  const ADVariableGradient & _grad_uy;
};